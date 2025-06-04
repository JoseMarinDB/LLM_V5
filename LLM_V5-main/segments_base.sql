-- ───────────────────────────────────────────────────────────────
-- 1. Parámetros
-- ───────────────────────────────────────────────────────────────

DECLARE ref_from DATE DEFAULT '{ref_from}';
DECLARE ref_to   DATE DEFAULT '{ref_to}';

DECLARE act_from DATE DEFAULT '{act_from}';
DECLARE act_to   DATE DEFAULT '{act_to}';

DECLARE country  STRING DEFAULT '{country}';


-- ───────────────────────────────────────────────────────────────
-- 2. CTEs con los KPI de referencia y actualidad
-- ───────────────────────────────────────────────────────────────
WITH ref AS (
  SELECT
    CASE 
      WHEN partner.vertical_group = 'Local Stores' AND partner.vertical_type = 'Market'
      THEN 'Local Stores (Market)' 
      ELSE partner.vertical_group 
    END                       AS vertical,
    COALESCE(partner.partner_classification,      'UNKNOWN') AS classification,
    COALESCE(partner.main_cousine_category_name,  'UNKNOWN') AS cuisine,

    COUNT(order_id)                                           AS orders_ref,
    SUM(gmv.gfv_vendor)                                       AS gfv_ref,
    SUM(gmv.basket_size)                                      AS qty_ref,
    ABS( SUM(COALESCE(basket_incentives,0))
       + SUM(COALESCE(plus_incentives,0))
       + SUM(COALESCE(people_incentives,0)) )                 AS incent_ref
  FROM `peya-datamarts-pro.dm_order_profitability.fact_order_profitability`
  WHERE registered_date BETWEEN ref_from AND ref_to
    AND order_status = 'CONFIRMED'
    AND location.country_name_en = country
  GROUP BY 1,2,3
),
act AS (
  SELECT
    CASE 
      WHEN partner.vertical_group = 'Local Stores' AND partner.vertical_type = 'Market'
      THEN 'Local Stores (Market)' 
      ELSE partner.vertical_group 
    END                       AS vertical,
    COALESCE(partner.partner_classification,      'UNKNOWN') AS classification,
    COALESCE(partner.main_cousine_category_name,  'UNKNOWN') AS cuisine,

    COUNT(order_id)                                           AS orders_act,
    SUM(gmv.gfv_vendor)                                       AS gfv_act,
    SUM(gmv.basket_size)                                      AS qty_act,
    ABS( SUM(COALESCE(basket_incentives,0))
       + SUM(COALESCE(plus_incentives,0))
       + SUM(COALESCE(people_incentives,0)) )                 AS incent_act
  FROM `peya-datamarts-pro.dm_order_profitability.fact_order_profitability`
  WHERE registered_date BETWEEN act_from AND act_to
    AND order_status = 'CONFIRMED'
    AND location.country_name_en = country
  GROUP BY 1,2,3
),

kpi AS (
  SELECT
    COALESCE(a.vertical,       r.vertical)       AS vertical,
    COALESCE(a.classification, r.classification) AS classification,
    COALESCE(a.cuisine,        r.cuisine)        AS cuisine,

    IFNULL(r.orders_ref, 0) AS orders_ref,
    IFNULL(r.gfv_ref,    0) AS gfv_ref,
    IFNULL(r.qty_ref,    0) AS qty_ref,
    IFNULL(r.incent_ref, 0) AS incent_ref,

    IFNULL(a.orders_act, 0) AS orders_act,
    IFNULL(a.gfv_act,    0) AS gfv_act,
    IFNULL(a.qty_act,    0) AS qty_act,
    IFNULL(a.incent_act, 0) AS incent_act
  FROM ref r
  FULL OUTER JOIN act a USING (vertical, classification, cuisine)
),

-- ───────────────────────────────────────────────────────────────
-- 3. Totales para el denominador (ACTUALIZADO con totales de ÓRDENES)
-- ───────────────────────────────────────────────────────────────
tot_country_act AS (
  SELECT SUM(gfv_act) AS gfv_act_tot, SUM(orders_act) AS orders_act_tot -- Añadido total de órdenes
  FROM kpi
),
tot_vertical_act AS (
  SELECT vertical, SUM(gfv_act) AS gfv_act_vertical, SUM(orders_act) AS orders_act_vertical -- Añadido total de órdenes
  FROM kpi
  GROUP BY vertical
),
-- tot_segment_act CTE no se usa actualmente para los denominadores de share_local.

-- CTEs para totales del período de Referencia (con ÓRDENES)
tot_country_ref AS (
  SELECT SUM(gfv_ref) AS gfv_ref_tot, SUM(orders_ref) AS orders_ref_tot -- Añadido total de órdenes
  FROM kpi
),
tot_vertical_ref AS (
  SELECT vertical, SUM(gfv_ref) AS gfv_ref_vertical, SUM(orders_ref) AS orders_ref_vertical -- Añadido total de órdenes
  FROM kpi
  GROUP BY vertical
)

-- ───────────────────────────────────────────────────────────────
-- 4. Árbol de segmentación + share country + share local (BASADO EN ÓRDENES)
-- ───────────────────────────────────────────────────────────────
-- 4-a. OVERALL
SELECT
  'OVERALL'     AS nivel1,
  NULL          AS nivel2,
  NULL          AS nivel3,

  SUM(orders_ref)   AS orders_ref,
  SUM(gfv_ref)      AS gfv_ref,
  SUM(qty_ref)      AS qty_ref,
  SUM(incent_ref)   AS incent_ref,

  SUM(orders_act)   AS orders_act,
  SUM(gfv_act)      AS gfv_act,
  SUM(qty_act)      AS qty_act,
  SUM(incent_act)   AS incent_act,
  
  (SUM(gfv_act) - SUM(gfv_ref)) AS delta_gfv, -- Delta GFV se mantiene igual

  1.0               AS share_act_orders_country, -- Share de Órdenes
  1.0               AS share_ref_orders_country, -- Share de Órdenes REF
  1.0               AS share_act_orders_local,   -- Share de Órdenes
  1.0               AS share_ref_orders_local    -- Share de Órdenes REF
FROM kpi

UNION ALL
-- 4-b. VERTICAL
SELECT
  'VERTICAL'    AS nivel1,
  k.vertical    AS nivel2,
  NULL          AS nivel3,

  SUM(k.orders_ref)   AS orders_ref,
  SUM(k.gfv_ref)      AS gfv_ref,
  SUM(k.qty_ref)      AS qty_ref,
  SUM(k.incent_ref)   AS incent_ref,

  SUM(k.orders_act)   AS orders_act,
  SUM(k.gfv_act)      AS gfv_act,
  SUM(k.qty_act)      AS qty_act,
  SUM(k.incent_act)   AS incent_act,

  (SUM(k.gfv_act) - SUM(k.gfv_ref)) AS delta_gfv,

  SAFE_DIVIDE(SUM(k.orders_act), tca.orders_act_tot) AS share_act_orders_country,
  SAFE_DIVIDE(SUM(k.orders_ref), tcr.orders_ref_tot) AS share_ref_orders_country,
  SAFE_DIVIDE(SUM(k.orders_act), tca.orders_act_tot) AS share_act_orders_local, 
  SAFE_DIVIDE(SUM(k.orders_ref), tcr.orders_ref_tot) AS share_ref_orders_local
FROM kpi k
CROSS JOIN tot_country_act tca
CROSS JOIN tot_country_ref tcr
GROUP BY k.vertical, tca.gfv_act_tot, tcr.gfv_ref_tot, tca.orders_act_tot, tcr.orders_ref_tot -- Añadido totales de órdenes al GROUP BY

UNION ALL
-- 4-c. SEGMENT  (vertical + classification)
SELECT
  'SEGMENT'         AS nivel1,
  k.vertical        AS nivel2,
  k.classification  AS nivel3,

  SUM(k.orders_ref)   AS orders_ref,
  SUM(k.gfv_ref)      AS gfv_ref,
  SUM(k.qty_ref)      AS qty_ref,
  SUM(k.incent_ref)   AS incent_ref,

  SUM(k.orders_act)   AS orders_act,
  SUM(k.gfv_act)      AS gfv_act,
  SUM(k.qty_act)      AS qty_act,
  SUM(k.incent_act)   AS incent_act,

  (SUM(k.gfv_act) - SUM(k.gfv_ref)) AS delta_gfv,

  SAFE_DIVIDE(SUM(k.orders_act), tca.orders_act_tot)          AS share_act_orders_country,
  SAFE_DIVIDE(SUM(k.orders_ref), tcr.orders_ref_tot)          AS share_ref_orders_country,
  SAFE_DIVIDE(SUM(k.orders_act), vta.orders_act_vertical)     AS share_act_orders_local, 
  SAFE_DIVIDE(SUM(k.orders_ref), vtr.orders_ref_vertical)     AS share_ref_orders_local
FROM kpi k
JOIN tot_vertical_act vta ON k.vertical = vta.vertical
JOIN tot_vertical_ref vtr ON k.vertical = vtr.vertical
CROSS JOIN tot_country_act tca
CROSS JOIN tot_country_ref tcr
GROUP BY k.vertical, k.classification, 
         vta.gfv_act_vertical, vtr.gfv_ref_vertical, tca.gfv_act_tot, tcr.gfv_ref_tot, -- Mantener gfv totals por si se usan en otro lado, aunque no para estos shares
         vta.orders_act_vertical, vtr.orders_ref_vertical, tca.orders_act_tot, tcr.orders_ref_tot -- Añadido totales de órdenes al GROUP BY

UNION ALL
-- 4-d. COCINA  (por vertical + cuisine, independiente de segmento)
SELECT
  'COCINA'          AS nivel1,
  k.vertical        AS nivel2,
  k.cuisine         AS nivel3,

  SUM(k.orders_ref)   AS orders_ref,
  SUM(k.gfv_ref)      AS gfv_ref,
  SUM(k.qty_ref)      AS qty_ref,
  SUM(k.incent_ref)   AS incent_ref,

  SUM(k.orders_act)   AS orders_act,
  SUM(k.gfv_act)      AS gfv_act,
  SUM(k.qty_act)      AS qty_act,
  SUM(k.incent_act)   AS incent_act,

  (SUM(k.gfv_act) - SUM(k.gfv_ref)) AS delta_gfv,

  SAFE_DIVIDE(SUM(k.orders_act), tca.orders_act_tot)          AS share_act_orders_country,
  SAFE_DIVIDE(SUM(k.orders_ref), tcr.orders_ref_tot)          AS share_ref_orders_country,
  SAFE_DIVIDE(SUM(k.orders_act), vta.orders_act_vertical)     AS share_act_orders_local, 
  SAFE_DIVIDE(SUM(k.orders_ref), vtr.orders_ref_vertical)     AS share_ref_orders_local
FROM kpi k
JOIN tot_vertical_act vta ON k.vertical = vta.vertical
JOIN tot_vertical_ref vtr ON k.vertical = vtr.vertical
CROSS JOIN tot_country_act tca
CROSS JOIN tot_country_ref tcr
GROUP BY k.vertical, k.cuisine, 
         vta.gfv_act_vertical, vtr.gfv_ref_vertical, tca.gfv_act_tot, tcr.gfv_ref_tot, -- Mantener gfv totals
         vta.orders_act_vertical, vtr.orders_ref_vertical, tca.orders_act_tot, tcr.orders_ref_tot -- Añadido totales de órdenes al GROUP BY

-- ───────────────────────────────────────────────────────────────
ORDER BY
  CASE nivel1
    WHEN 'OVERALL'  THEN 1
    WHEN 'VERTICAL' THEN 2
    WHEN 'SEGMENT'  THEN 3
    WHEN 'COCINA'   THEN 4
  END,
  nivel2,
  nivel3;