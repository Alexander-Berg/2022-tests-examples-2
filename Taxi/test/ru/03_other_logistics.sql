/*============================================================
 Other Logistics
============================================================*/
-- Размазываем план по Лавкам пропорционально количеству пришедших на них новичков
CREATE TEMPORARY TABLE ol_plan_spread
ON COMMIT DROP
AS (
  SELECT nc.lcl_calculation_dt
    , nc.country_name
    , nc.region_name
    , nc.store_id
    , nc.month_dt
    , mc.other_logistics_plan_lcy
        * nc.days_in_month_passed
        / nc.days_in_month
        / nc.new_courier_full_month_cnt
        * nc.new_courier_cnt AS other_logistics_value_lcy
  FROM {stg_new_courier} AS nc
  LEFT JOIN {stg_manual_correction} AS mc
    ON nc.month_dt = mc.month_dt
    AND nc.country_name = mc.country_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE ol_plan_spread;

-- Обогащаем предыдущую таблицу так, чтобы данных хватило для расчета статей
CREATE TEMPORARY TABLE ol_plan_spread_enriched
ON COMMIT DROP
AS (
  SELECT p.lcl_calculation_dt
    , p.country_name
    , p.region_name
    , p.store_id
    , p.other_logistics_value_lcy
    , SUM(p.other_logistics_value_lcy) OVER w AS other_logistics_full_month_value_lcy
    , rv.other_logistics_reserve_value_lcy
    , p.month_dt
  FROM ol_plan_spread AS p
  LEFT JOIN {stg_reserve} AS rv
    ON p.month_dt = rv.month_dt
    AND p.country_name = rv.country_name
  WINDOW w AS (PARTITION BY p.month_dt, p.country_name)
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE ol_plan_spread_enriched;

------------------------------
-- Other Logistics
------------------------------
CREATE TEMPORARY TABLE pre_stg_other_logistics
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- План (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , e.other_logistics_value_lcy
        / cr.lcl_to_rub::NUMERIC                AS other_logistics_value_lcy

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.other_logistics_fact_lcy
                 * e.other_logistics_value_lcy
                 / e.other_logistics_full_month_value_lcy
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS other_logistics_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.other_logistics_reserve_value_lcy IS NOT NULL
        AND e.other_logistics_reserve_value_lcy != 0
          THEN e.other_logistics_reserve_value_lcy
                 * e.other_logistics_value_lcy
                 / e.other_logistics_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS other_logistics_reserve_value_lcy

    , mc.fiscal_year_closed_period_flg
  FROM ol_plan_spread_enriched AS e
  LEFT JOIN {stg_manual_correction} AS mc
    ON e.month_dt = mc.month_dt
    AND e.country_name = mc.country_name
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
  WHERE e.country_name IN ('Россия')
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_other_logistics;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_other_logistics}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , other_logistics_value_lcy
    , other_logistics_from_finance_department_value_lcy
    , other_logistics_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "план + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN other_logistics_from_finance_department_value_lcy
        ELSE other_logistics_value_lcy + other_logistics_reserve_value_lcy
      END::NUMERIC                          AS other_logistics_final_w_reserve_value_lcy

  FROM pre_stg_other_logistics
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                          AS other_logistics_value_lcy
    , other_logistics_unallocated_value_rub AS other_logistics_from_finance_department_value_lcy
    , '0'::NUMERIC                          AS other_logistics_reserve_value_lcy
    , other_logistics_unallocated_value_rub AS other_logistics_final_w_reserve_value_lcy
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_other_logistics};
GRANT ALL ON {stg_other_logistics} TO "ed-avetisyan";
GRANT ALL ON {stg_other_logistics} TO agabitashvili;
GRANT ALL ON {stg_other_logistics} TO "robot-lavka-analyst";
