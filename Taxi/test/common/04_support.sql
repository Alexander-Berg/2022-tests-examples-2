------------------------------
-- Support
------------------------------
CREATE TEMPORARY TABLE pre_stg_support
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- План (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , mc.support_plan_lcy
        * e.days_in_month_passed
        / e.days_in_month
        * e.clear_orders_cnt
        / e.clear_orders_full_month_cnt
        / cr.lcl_to_rub::NUMERIC                AS support_value_lcy

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.support_fact_lcy
                 * e.clear_orders_cnt
                 / e.clear_orders_full_month_cnt
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS support_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.support_reserve_value_lcy IS NOT NULL
        AND e.support_reserve_value_lcy != 0
          THEN e.support_reserve_value_lcy
                 * e.clear_orders_cnt
                 / e.clear_orders_full_month_cnt
        ELSE 0.0
      END::NUMERIC                              AS support_reserve_value_lcy

    , mc.fiscal_year_closed_period_flg
  FROM {stg_agg_pnl_enriched} AS e
  LEFT JOIN {stg_manual_correction} AS mc
    ON e.month_dt = mc.month_dt
    AND e.country_name = mc.country_name
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_support;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_support}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , support_value_lcy
    , support_from_finance_department_value_lcy
    , support_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "план + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN support_from_finance_department_value_lcy
        ELSE support_value_lcy + support_reserve_value_lcy
      END::NUMERIC                  AS support_final_w_reserve_value_lcy

  FROM pre_stg_support
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                  AS support_value_lcy
    , support_unallocated_value_rub AS support_from_finance_department_value_lcy
    , '0'::NUMERIC                  AS support_reserve_value_lcy
    , support_unallocated_value_rub AS support_final_w_reserve_value_lcy
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_support};
GRANT ALL ON {stg_support} TO "ed-avetisyan";
GRANT ALL ON {stg_support} TO agabitashvili;
GRANT ALL ON {stg_support} TO "robot-lavka-analyst";
