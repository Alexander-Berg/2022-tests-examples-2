/*=========================================================
 Разбираемся с manual_correction_by_place:
   - Придумываем помесячный план
   - Размазываем помесячный план и факт по дням
=========================================================*/
-- Юнионим и обогащаем словари (сейчас здесь только Россия, потом добавится Израиль)
CREATE TEMPORARY TABLE mc_by_place_fact_monthly
ON COMMIT DROP
AS (
  SELECT mc.month_dt
    , (mc.month_dt + '1 month'::INTERVAL)::DATE                         AS month_ahead_dt
    , (mc.month_dt + '2 month'::INTERVAL)::DATE                         AS two_months_ahead_dt
    , s.country_name
    , s.region_name
    , mc.store_id
    , mc.people_cost_lcy
    , mc.rent_value_lcy
    , mc.utilities_value_lcy
    , EXTRACT(
        DAYS FROM mc.month_dt + '1 month - 1 day'::INTERVAL
      )                                                                 AS days_in_month
  FROM (
    SELECT month_dt
      , place_id::VARCHAR AS store_id
      , people_cost_lcy
      , rent_value_lcy
      , utilities_value_lcy
    FROM {pnl_ru_manual_correction_by_place}
  ) AS mc
  JOIN {stg_store} AS s
    ON mc.store_id = s.store_id
) DISTRIBUTED BY (month_ahead_dt, store_id);
ANALYZE mc_by_place_fact_monthly;

-- Рассчитываем средние значения по регионам
CREATE TEMPORARY TABLE avg_per_region
ON COMMIT DROP
AS (
  SELECT month_ahead_dt
    , region_name
    , AVG(people_cost_lcy)     AS people_cost_lcy
    , AVG(rent_value_lcy)      AS rent_value_lcy
    , AVG(utilities_value_lcy) AS utilities_value_lcy
  FROM mc_by_place_fact_monthly
  GROUP BY 1, 2
) DISTRIBUTED BY (month_ahead_dt, region_name);
ANALYZE avg_per_region;

-- Рассчитываем средние значения по странам
CREATE TEMPORARY TABLE avg_per_country
ON COMMIT DROP
AS (
  SELECT month_ahead_dt
    , country_name
    , AVG(people_cost_lcy)     AS people_cost_lcy
    , AVG(rent_value_lcy)      AS rent_value_lcy
    , AVG(utilities_value_lcy) AS utilities_value_lcy
  FROM mc_by_place_fact_monthly
  GROUP BY 1, 2
) DISTRIBUTED BY (month_ahead_dt, country_name);
ANALYZE avg_per_country;

-- Формируем помесячные планы для Лавок [
CREATE TEMPORARY TABLE stores_w_orders
ON COMMIT DROP
AS (
  -- 1. Находим связки "месяц + Лавка" с ненулевыми заказами
  SELECT o.lcl_order_created_dt AS month_dt
    , s.country_name
    , s.region_name
    , o.place_id                AS store_id
  FROM {agg_lavka_order_monthly} AS o
  JOIN {stg_store} AS s
    ON o.place_id = s.store_id
  WHERE o.order_cnt > 0
    AND s.country_name IN ('Россия')
) DISTRIBUTED BY (month_dt, store_id);
ANALYZE stores_w_orders;

CREATE TEMPORARY TABLE mc_by_place_plan_monthly
ON COMMIT DROP
AS (
  /*
  2. Определяем, какое значение должно лежать в плане:
   - Если Лавка первая в регионе, то плановое значение на текущий месяц - это среднее по стране за прошлый месяц
   - Если это обычная новая Лавка (в регионе есть старые Лавки), то берем среднюю аренду всех Лавок по региону за прошлый месяц
   - Если это старая Лавка, то пытаемся взять факт для этой Лавки из прошлого месяца
   - Если это старая Лавка, и прошлого месяца нет, то берем факт из позапрошлого месяца
  */
  SELECT s.month_dt
    , s.country_name
    , s.region_name
    , s.store_id
    , COALESCE(
        mc_1.people_cost_lcy
        , mc_2.people_cost_lcy
        , ar.people_cost_lcy
        , ac.people_cost_lcy
        , 0
      )                                                                 AS people_cost_lcy
    , CASE
        WHEN mc_1.people_cost_lcy IS NOT NULL THEN '{txt_plan_prev_month}'
        WHEN mc_2.people_cost_lcy IS NOT NULL THEN '{txt_plan_preprev_month}'
        WHEN ar.people_cost_lcy IS NOT NULL THEN '{txt_plan_avg_region}'
        WHEN ac.people_cost_lcy IS NOT NULL THEN '{txt_plan_avg_country}'
        ELSE '{txt_incalculable}'
      END::VARCHAR                                                      AS people_cost_plan_method_name
    , COALESCE(
        mc_1.rent_value_lcy
        , mc_2.rent_value_lcy
        , ar.rent_value_lcy
        , ac.rent_value_lcy
        , 0
      )                                                                 AS rent_value_lcy
    , CASE
        WHEN mc_1.rent_value_lcy IS NOT NULL THEN '{txt_plan_prev_month}'
        WHEN mc_2.rent_value_lcy IS NOT NULL THEN '{txt_plan_preprev_month}'
        WHEN ar.rent_value_lcy IS NOT NULL THEN '{txt_plan_avg_region}'
        WHEN ac.rent_value_lcy IS NOT NULL THEN '{txt_plan_avg_country}'
        ELSE '{txt_incalculable}'
      END::VARCHAR                                                      AS rent_plan_method_name
    , COALESCE(
        mc_1.utilities_value_lcy
        , mc_2.utilities_value_lcy
        , ar.utilities_value_lcy
        , ac.utilities_value_lcy
        , 0
      )                                                                 AS utilities_value_lcy
    , CASE
        WHEN mc_1.utilities_value_lcy IS NOT NULL THEN '{txt_plan_prev_month}'
        WHEN mc_2.utilities_value_lcy IS NOT NULL THEN '{txt_plan_preprev_month}'
        WHEN ar.utilities_value_lcy IS NOT NULL THEN '{txt_plan_avg_region}'
        WHEN ac.utilities_value_lcy IS NOT NULL THEN '{txt_plan_avg_country}'
        ELSE '{txt_incalculable}'
      END::VARCHAR                                                      AS utilities_plan_method_name
    , EXTRACT(
        DAYS FROM s.month_dt + '1 month - 1 day'::INTERVAL
      )                                                                 AS days_in_month
  FROM stores_w_orders AS s
  LEFT JOIN mc_by_place_fact_monthly AS mc_1
       ON s.store_id = mc_1.store_id
         AND s.month_dt = mc_1.month_ahead_dt
  LEFT JOIN mc_by_place_fact_monthly AS mc_2
       ON s.store_id = mc_2.store_id
         AND s.month_dt = mc_2.two_months_ahead_dt
  LEFT JOIN avg_per_region AS ar
       ON s.region_name = ar.region_name
         AND s.month_dt = ar.month_ahead_dt
  LEFT JOIN avg_per_country AS ac
       ON s.country_name = ac.country_name
         AND s.month_dt = ac.month_ahead_dt
) DISTRIBUTED BY (month_dt, store_id);
ANALYZE mc_by_place_plan_monthly;
-- ] Формируем помесячные планы для Лавок

-- Размазываем план по дням
CREATE TEMPORARY TABLE mc_by_place_plan_daily
ON COMMIT DROP
AS (
  -- 2. Оставляем дневные планы только для тех дат, на которых есть заказы
  SELECT mc.*
  FROM (
    -- 1. Вычисляем дневные константы
    SELECT country_name
      , region_name
      , store_id
      , generate_series(
          month_dt, (month_dt + '1 month - 1 day'::INTERVAL)::DATE, '1 day'::INTERVAL
        )::DATE                                                              AS lcl_calculation_dt
      , month_dt
      , people_cost_lcy / days_in_month                                      AS people_cost_lcy
      , people_cost_plan_method_name
      , rent_value_lcy / days_in_month                                       AS rent_value_lcy
      , rent_plan_method_name
      , utilities_value_lcy / days_in_month                                  AS utilities_value_lcy
      , utilities_plan_method_name
    FROM mc_by_place_plan_monthly
  ) AS mc
  JOIN {stg_agg_pnl_w_regions} AS p
       ON mc.lcl_calculation_dt = p.lcl_event_dt
         AND mc.store_id = p.place_id::VARCHAR
  WHERE mc.lcl_calculation_dt < CURRENT_DATE
    AND p.order_cnt > 0
) DISTRIBUTED BY (lcl_calculation_dt, store_id);
ANALYZE mc_by_place_plan_daily;

-- Размазываем факт по дням равномерным слоем
CREATE TEMPORARY TABLE mc_by_place_fact_daily
ON COMMIT DROP
AS (
  SELECT *
  FROM (
    SELECT country_name
      , region_name
      , store_id
      , generate_series(
          month_dt, (month_dt + '1 month - 1 day'::INTERVAL)::DATE, '1 day'::INTERVAL
        )::DATE                                                              AS lcl_calculation_dt
      , month_dt
      , people_cost_lcy / days_in_month                                      AS people_cost_lcy
      , rent_value_lcy / days_in_month                                       AS rent_value_lcy
      , utilities_value_lcy / days_in_month                                  AS utilities_value_lcy
    FROM mc_by_place_fact_monthly
  ) AS mc
  WHERE lcl_calculation_dt < CURRENT_DATE
) DISTRIBUTED BY (lcl_calculation_dt, store_id);
ANALYZE mc_by_place_fact_daily;

-- Слепляем воедино план и факт
CREATE TEMPORARY TABLE mc_by_place_daily
ON COMMIT DROP
AS (
  SELECT COALESCE(p.lcl_calculation_dt, f.lcl_calculation_dt) AS lcl_calculation_dt
    , COALESCE(p.country_name, f.country_name)                AS country_name
    , COALESCE(p.region_name, f.region_name)                  AS region_name
    , COALESCE(p.store_id, f.store_id)                        AS store_id
    , COALESCE(p.month_dt, f.month_dt)                        AS month_dt
    , p.people_cost_lcy                                       AS people_cost_plan_lcy
    , f.people_cost_lcy                                       AS people_cost_fact_lcy
    , p.people_cost_plan_method_name
    , p.rent_value_lcy                                        AS rent_plan_value_lcy
    , f.rent_value_lcy                                        AS rent_fact_value_lcy
    , p.rent_plan_method_name
    , p.utilities_value_lcy                                   AS utilities_plan_value_lcy
    , f.utilities_value_lcy                                   AS utilities_fact_value_lcy
    , p.utilities_plan_method_name
  FROM mc_by_place_plan_daily AS p
  FULL JOIN mc_by_place_fact_daily AS f
       ON p.lcl_calculation_dt = f.lcl_calculation_dt
         AND p.store_id = f.store_id
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE mc_by_place_daily;

-- Обогащаем эту табличку резервами
DROP TABLE IF EXISTS {stg_mc_by_place_enriched};
CREATE TABLE {stg_mc_by_place_enriched}
AS (
  SELECT mc.lcl_calculation_dt
    , mc.country_name
    , mc.region_name
    , mc.store_id
    , mc.people_cost_plan_lcy
    , SUM(mc.people_cost_plan_lcy) OVER w     AS people_cost_plan_full_month_lcy
    , mc.people_cost_fact_lcy
    , mc.people_cost_plan_method_name
    , rv.people_cost_reserve_value_lcy
    , mc.rent_plan_value_lcy
    , SUM(mc.rent_plan_value_lcy) OVER w      AS rent_plan_full_month_value_lcy
    , mc.rent_fact_value_lcy
    , mc.rent_plan_method_name
    , rv.rent_reserve_value_lcy
    , mc.utilities_plan_value_lcy
    , SUM(mc.utilities_plan_value_lcy) OVER w AS utilities_plan_full_month_value_lcy
    , mc.utilities_fact_value_lcy
    , mc.utilities_plan_method_name
    , rv.utilities_reserve_value_lcy
  FROM mc_by_place_daily AS mc
  LEFT JOIN {stg_reserve} AS rv
       ON mc.month_dt = rv.month_dt
         AND mc.country_name = rv.country_name
  WINDOW w AS (PARTITION BY mc.month_dt, mc.country_name)
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_mc_by_place_enriched};
GRANT ALL ON {stg_mc_by_place_enriched} TO "ed-avetisyan";
GRANT ALL ON {stg_mc_by_place_enriched} TO agabitashvili;
GRANT ALL ON {stg_mc_by_place_enriched} TO "robot-lavka-analyst";
