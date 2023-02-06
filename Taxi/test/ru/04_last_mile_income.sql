------------------------------
-- Last Mile Income
------------------------------
CREATE TEMPORARY TABLE pre_stg_last_mile_income
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- Прогноз на основе general_constant (рассчитан уже в локальной валюте, поэтому переводить не нужно)
    , e.last_mile_income_value_lcy::NUMERIC     AS last_mile_income_value_lcy

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.last_mile_revenue_fact_value_lcy
                 * e.last_mile_income_value_lcy
                 / e.last_mile_income_full_month_value_lcy
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS last_mile_income_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.last_mile_income_reserve_value_lcy IS NOT NULL
        AND e.last_mile_income_reserve_value_lcy != 0
          THEN e.last_mile_income_reserve_value_lcy
                 * e.last_mile_income_value_lcy
                 / e.last_mile_income_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS last_mile_income_reserve_value_lcy

    , mc.fiscal_year_closed_period_flg
  FROM {stg_agg_pnl_enriched} AS e
  LEFT JOIN {stg_manual_correction} AS mc
    ON e.month_dt = mc.month_dt
    AND e.country_name = mc.country_name
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
  WHERE e.country_name IN ('Россия')
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_last_mile_income;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_last_mile_income}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , last_mile_income_value_lcy
    , last_mile_income_from_finance_department_value_lcy
    , last_mile_income_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "прогноз + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN last_mile_income_from_finance_department_value_lcy
        ELSE last_mile_income_value_lcy + last_mile_income_reserve_value_lcy
      END::NUMERIC                            AS last_mile_income_final_w_reserve_value_lcy

  FROM pre_stg_last_mile_income
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                            AS last_mile_income_value_lcy
    , last_mile_revenue_unallocated_value_rub AS last_mile_income_from_finance_department_value_lcy
    , '0'::NUMERIC                            AS last_mile_income_reserve_value_lcy
    , last_mile_revenue_unallocated_value_rub AS last_mile_income_final_w_reserve_value_lcy
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_last_mile_income};
GRANT ALL ON {stg_last_mile_income} TO "ed-avetisyan";
GRANT ALL ON {stg_last_mile_income} TO agabitashvili;
GRANT ALL ON {stg_last_mile_income} TO "robot-lavka-analyst";
