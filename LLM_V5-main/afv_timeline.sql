-- 1. Parámetros
-- ───────────────────────────────────────────────────────────────
-- Indicar cualquier fecha dentro del MES MÁS RECIENTE que se quiere analizar.
-- Por ejemplo, si pones '2025-02-10', el mes más reciente será Febrero 2025.
DECLARE report_most_recent_month_indicator DATE DEFAULT '{act_to}'; 
DECLARE country_filter STRING DEFAULT '{country}';

-- Número total de meses a mostrar (incluyendo el más reciente y los anteriores)
-- Si quieres el mes actual + los 4 anteriores = 5 meses en total.
DECLARE num_total_months_to_display INT64 DEFAULT {num_total_months_to_display}; 
-- ───────────────────────────────────────────────────────────────
-- 2. CTE para generar la lista de meses a calcular
-- ───────────────────────────────────────────────────────────────
WITH months_to_calculate AS (
  SELECT month_start_date
  FROM UNNEST(GENERATE_DATE_ARRAY(
    DATE_TRUNC(DATE_SUB(DATE_TRUNC(report_most_recent_month_indicator, MONTH), INTERVAL (num_total_months_to_display - 1) MONTH), MONTH), -- Fecha de inicio del primer mes en el rango
    DATE_TRUNC(report_most_recent_month_indicator, MONTH), -- Fecha de inicio del último mes (el más reciente) en el rango
    INTERVAL 1 MONTH -- Intervalo para generar los meses
  )) AS month_start_date
),

-- ───────────────────────────────────────────────────────────────
-- 3. CTE para calcular AFV para cada mes y vertical
-- ───────────────────────────────────────────────────────────────
monthly_afv_data AS (
  SELECT
    m.month_start_date AS month_date,
    CASE
      WHEN fop.partner.vertical_group = 'Local Stores' AND fop.partner.vertical_type = 'Market'
      THEN 'Local Stores (Market)'
      ELSE fop.partner.vertical_group
    END AS vertical,
    SUM(fop.gmv.gfv_vendor) AS total_gfv,
    COUNT(fop.order_id) AS total_orders
  FROM 
    months_to_calculate AS m
  JOIN 
    `peya-datamarts-pro.dm_order_profitability.fact_order_profitability` AS fop
    ON DATE_TRUNC(fop.registered_date, MONTH) = m.month_start_date -- Unimos los pedidos al mes correspondiente
  WHERE 
    fop.order_status = 'CONFIRMED'
    AND fop.location.country_name_en = country_filter
    -- No es necesario filtrar fop.registered_date por rango aquí, ya que el JOIN a months_to_calculate lo limita.
    -- Sin embargo, si la tabla fop es muy grande y no está particionada por registered_date, 
    -- un filtro explícito podría ayudar en algunos motores de BD, pero para BigQuery el JOIN es eficiente.
    -- Si fuera necesario: AND fop.registered_date BETWEEN m.month_start_date AND LAST_DAY(m.month_start_date, MONTH) 
  GROUP BY 
    m.month_start_date,
    vertical
)

-- ───────────────────────────────────────────────────────────────
-- 4. Selección final con el cálculo de AFV
-- ───────────────────────────────────────────────────────────────
SELECT
  vertical,
  month_date,
  ROUND(SAFE_DIVIDE(total_gfv, total_orders),2) AS afv
FROM monthly_afv_data
where vertical != "Courier"
ORDER BY
  vertical,
  month_date DESC; -- Mostrar primero los meses más recientes