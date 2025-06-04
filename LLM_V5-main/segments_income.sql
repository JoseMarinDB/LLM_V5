-- ───────────────────────────────────────────────────────────────
-- 1. Parámetros
-- ───────────────────────────────────────────────────────────────

DECLARE ref_from DATE DEFAULT '{ref_from}'; -- Fecha de inicio del período de referencia
DECLARE ref_to   DATE DEFAULT '{ref_to}';   -- Fecha de fin del período de referencia

DECLARE act_from DATE DEFAULT '{act_from}'; -- Fecha de inicio del período actual/activo
DECLARE act_to   DATE DEFAULT '{act_to}';   -- Fecha de fin del período actual/activo

DECLARE country  STRING DEFAULT '{country}'; -- País para filtrar los datos

-- 2. Período ACTUAL ────────────────────────────────────────────────────
WITH actual AS (
  SELECT
    COALESCE(fop.user.income, 'UNKNOWN')              AS segmento ,
    COUNT(order_id)                                   AS ordenes_act ,
    SUM(gmv.gfv_vendor)                               AS gfv_act
  FROM `peya-datamarts-pro.dm_order_profitability.fact_order_profitability` fop
  WHERE fop.partner.vertical_group IN ('D-Mart', 'Food', 'Local Stores')
    AND fop.registered_date BETWEEN act_from AND act_to
    AND fop.location.country_name_en = country
    AND fop.order_status = 'CONFIRMED'
  GROUP BY segmento
),

-- 3. Período REFERENCIA ────────────────────────────────────────────────
ref AS (
  SELECT
    COALESCE(fop.user.income, 'UNKNOWN')              AS segmento ,
    COUNT(order_id)                                   AS ordenes_ref ,
    SUM(gmv.gfv_vendor)                               AS gfv_ref
  FROM `peya-datamarts-pro.dm_order_profitability.fact_order_profitability` fop
  WHERE fop.partner.vertical_group IN ('D-Mart', 'Food', 'Local Stores')
    AND fop.registered_date BETWEEN ref_from AND ref_to
    AND fop.location.country_name_en = country
    AND fop.order_status = 'CONFIRMED'
  GROUP BY segmento
),

-- 4. Unión de ambos períodos ───────────────────────────────────────────
base AS (
  SELECT
    COALESCE(a.segmento , r.segmento)         AS segmento ,
    COALESCE(a.ordenes_act, 0)                AS ordenes_act ,
    COALESCE(a.gfv_act    , 0)                AS gfv_act ,
    COALESCE(r.ordenes_ref, 0)                AS ordenes_ref ,
    COALESCE(r.gfv_ref    , 0)                AS gfv_ref
  FROM actual a
  FULL OUTER JOIN ref r USING (segmento)
),

-- 5. Share (por órdenes) y AFV ─────────────────────────────────────────
calc AS (
  SELECT
    b.* ,
    SAFE_DIVIDE(b.gfv_act , NULLIF(b.ordenes_act ,0)) AS afv_act ,
    SAFE_DIVIDE(b.gfv_ref , NULLIF(b.ordenes_ref,0)) AS afv_ref ,
    ROUND( SAFE_DIVIDE(b.ordenes_act , SUM(b.ordenes_act) OVER()) *100 , 2) AS share_act ,
    ROUND( SAFE_DIVIDE(b.ordenes_ref , SUM(b.ordenes_ref) OVER()) *100 , 2) AS share_ref
  FROM base b
)

-- 6. Selección final ──────────────────────────────────────────────────
SELECT
  segmento ,
  ordenes_act , ordenes_ref ,
  afv_act     , afv_ref ,
  ROUND(afv_act - afv_ref, 2)                  AS delta_afv ,
  share_act   , share_ref ,
  ROUND(share_act - share_ref, 2)              AS dif_share_en_pp
FROM calc
WHERE segmento <> 'UNKNOWN'
ORDER BY dif_share_en_pp DESC;
