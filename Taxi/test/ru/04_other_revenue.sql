/*============================================================
 Other Revenue
============================================================*/
-- Размазывание статьи согласно GMV [
CREATE TEMPORARY TABLE agg_gmv
ON COMMIT DROP
AS (
  -- 1.1. Определяем GMV для каждой Лавки в каждый день
  SELECT lcl_event_dt
    , country_name
    , region_name
    , days_in_month
    , days_in_month_passed
    , place_id      AS store_id
    , gmv_w_vat_lcy AS gmv_fact
  FROM {stg_agg_pnl_w_regions}
  WHERE country_name IN ('Россия')
    AND region_name IN ('Санкт-Петербург', 'Москва')
) DISTRIBUTED BY (lcl_event_dt, region_name);
ANALYZE agg_gmv;

CREATE TEMPORARY TABLE sales_dict
ON COMMIT DROP
AS (
  -- 1.2. Определям, в какие дни в каждом из регионов были продажи
  SELECT lcl_event_dt
    , country_name
    , region_name
    , days_in_month
    , days_in_month_passed
  FROM agg_gmv
  GROUP BY 1, 2, 3, 4, 5
  HAVING SUM(gmv_fact) > 0
) DISTRIBUTED BY (lcl_event_dt, region_name);
ANALYZE sales_dict;

CREATE TEMPORARY TABLE forecasts_daily
ON COMMIT DROP
AS (
  -- 2.2. Разворачиваем недели в дни
  SELECT generate_series(plan_period_start_dt, plan_period_end_dt, '1 day'::INTERVAL)::DATE AS plan_dt
    , region_name
    , date_trunc('month', plan_period_end_dt)::DATE                                         AS month_dt
    , gmv_plan / (plan_period_end_dt - plan_period_start_dt + 1)                            AS gmv_plan
  FROM (
    -- 2.1. Вытаскиваем актуальные форкасты для каждой недели по каждому городу
    SELECT r.region_name                                               AS region_name
      , f.metric_period_start_dt                                       AS plan_period_start_dt
      , f.metric_period_end_dt                                         AS plan_period_end_dt
      , (array_agg(f.metric_val ORDER BY f.budget_version_dt DESC))[1] AS gmv_plan
    FROM {forecasts} AS f
    JOIN {stg_region_dict} AS r
      ON r.region_name = CASE -- ВНИМАНИЕ! КОСТЫЛЬ!!!
                           WHEN f.metric_city_name = 'Франшиза'
                             THEN 'Иркутск'
                           ELSE f.metric_city_name
                         END
    WHERE f.metric_period_d <= 7    -- Нас интересуют только недельные разрезы
      AND f.metric_name = 'GMV'
      AND r.country_name IN ('Россия')
      AND r.region_name IN ('Санкт-Петербург', 'Москва')
    GROUP BY 1, 2, 3
  ) AS g
) DISTRIBUTED BY (plan_dt, region_name);
ANALYZE forecasts_daily;

CREATE TEMPORARY TABLE other_revenue_by_cities
ON COMMIT DROP
AS (
  -- 4. Размазываем Other Revenue из manual_correction по городам и дням согласно доле планового GMV
  SELECT g.plan_dt
    , g.country_name
    , g.region_name
    , g.month_dt
    , g.gmv_plan_rate
    , mc.other_revenue_plan_lcy
        * g.days_in_month_passed
        / g.days_in_month
        * g.gmv_plan_rate::NUMERIC AS other_revenue_lcy
  FROM
  (
    -- 3. Для каждого города на каждый день с ненулевыми продажами находим долю планового GMV
    SELECT s.country_name
      , f.plan_dt
      , f.region_name
      , f.month_dt
      , f.gmv_plan / SUM(f.gmv_plan) OVER (PARTITION BY f.month_dt)                   AS gmv_plan_rate
      , s.days_in_month
      , s.days_in_month_passed
    FROM forecasts_daily AS f
    JOIN sales_dict AS s
         ON f.plan_dt = s.lcl_event_dt
           AND f.region_name = s.region_name
  ) AS g
  JOIN {stg_manual_correction} AS mc
       ON g.month_dt = mc.month_dt
         AND g.country_name = mc.country_name
) DISTRIBUTED BY (plan_dt, region_name);
ANALYZE other_revenue_by_cities;

CREATE TEMPORARY TABLE other_revenue_spread
ON COMMIT DROP
AS (
  -- 6. Вычисляем Other Revenue согласно доле фактического GMV
  SELECT r.plan_dt                                                    AS lcl_calculation_dt
    , g.country_name
    , g.region_name
    , g.store_id
    , date_trunc('month', r.plan_dt)::DATE                            AS month_dt
    , COALESCE(g.gmv_fact_rate, 0) * COALESCE(r.other_revenue_lcy, 0) AS other_revenue_value_lcy
  FROM (
    -- 5. Рассчитываем долю фактического GMV для каждой Лавки внутри дня
    SELECT region_name
      , country_name
      , store_id
      , lcl_event_dt
      , gmv_fact / SUM(gmv_fact) OVER (PARTITION BY lcl_event_dt, region_name) AS gmv_fact_rate
    FROM agg_gmv
  ) AS g
  JOIN other_revenue_by_cities AS r
       ON g.lcl_event_dt = r.plan_dt
         AND g.region_name = r.region_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE other_revenue_spread;
-- ] Конец размазывания

-- Обогащаем предыдущую таблицу так, чтобы данных хватило для расчета статей
CREATE TEMPORARY TABLE other_revenue_spread_enriched
ON COMMIT DROP
AS (
  SELECT s.lcl_calculation_dt
    , s.country_name
    , s.region_name
    , s.store_id
    , s.month_dt
    , s.other_revenue_value_lcy
    , SUM(s.other_revenue_value_lcy) OVER w AS other_revenue_full_month_value_lcy
    , rv.other_revenue_reserve_value_lcy
  FROM other_revenue_spread AS s
  LEFT JOIN {stg_reserve} AS rv
    ON s.month_dt = rv.month_dt
    AND s.country_name = rv.country_name
  WINDOW w AS (PARTITION BY s.month_dt, s.country_name)
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE other_revenue_spread_enriched;

------------------------------
-- Other Revenue
------------------------------
CREATE TEMPORARY TABLE pre_stg_other_revenue
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- План (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , e.other_revenue_value_lcy
        / cr.lcl_to_rub::NUMERIC                AS other_revenue_value_lcy

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.other_revenue_fact_lcy
                 * e.other_revenue_value_lcy
                 / e.other_revenue_full_month_value_lcy
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS other_revenue_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.other_revenue_reserve_value_lcy IS NOT NULL
        AND e.other_revenue_reserve_value_lcy != 0
          THEN e.other_revenue_reserve_value_lcy
                 * e.other_revenue_value_lcy
                 / e.other_revenue_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS other_revenue_reserve_value_lcy

    , mc.fiscal_year_closed_period_flg
  FROM other_revenue_spread_enriched AS e
  LEFT JOIN {stg_manual_correction} AS mc
    ON e.month_dt = mc.month_dt
    AND e.country_name = mc.country_name
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
  WHERE e.country_name IN ('Россия')
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_other_revenue;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_other_revenue}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , other_revenue_value_lcy
    , other_revenue_from_finance_department_value_lcy
    , other_revenue_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "план + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN other_revenue_from_finance_department_value_lcy
        ELSE other_revenue_value_lcy + other_revenue_reserve_value_lcy
      END::NUMERIC                        AS other_revenue_final_w_reserve_value_lcy

  FROM pre_stg_other_revenue
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                        AS other_revenue_value_lcy
    , other_revenue_unallocated_value_rub AS other_revenue_from_finance_department_value_lcy
    , '0'::NUMERIC                        AS other_revenue_reserve_value_lcy
    , other_revenue_unallocated_value_rub AS other_revenue_final_w_reserve_value_lcy
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_other_revenue};
GRANT ALL ON {stg_other_revenue} TO "ed-avetisyan";
GRANT ALL ON {stg_other_revenue} TO agabitashvili;
GRANT ALL ON {stg_other_revenue} TO "robot-lavka-analyst";
