------------------------------
-- Incentives
------------------------------
CREATE TEMPORARY TABLE pre_stg_incentives
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- Факт из источника (приходит уже в локальной валюте, поэтому переводить не нужно)
    , e.incentives_discount_value_lcy::NUMERIC
    , e.incentives_promocode_value_lcy::NUMERIC
    , e.incentives_cashback_amt::NUMERIC
    , e.incentives_value_lcy::NUMERIC

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.incentives_fact_value_lcy
                 * e.incentives_value_lcy
                 / e.incentives_full_month_value_lcy
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS incentives_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.incentives_reserve_value_lcy IS NOT NULL
        AND e.incentives_reserve_value_lcy != 0
          THEN e.incentives_reserve_value_lcy
                 * e.incentives_value_lcy
                 / e.incentives_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS incentives_reserve_value_lcy

    , mc.fiscal_year_closed_period_flg
  FROM {stg_agg_pnl_enriched} AS e
  LEFT JOIN {stg_manual_correction} AS mc
    ON e.month_dt = mc.month_dt
    AND e.country_name = mc.country_name
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_incentives;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_incentives}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , incentives_discount_value_lcy
    , incentives_promocode_value_lcy
    , incentives_cashback_amt
    , incentives_value_lcy
    , incentives_from_finance_department_value_lcy
    , incentives_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "факт + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN incentives_from_finance_department_value_lcy
        ELSE incentives_value_lcy + incentives_reserve_value_lcy
      END::NUMERIC                           AS incentives_final_w_reserve_value_lcy

  FROM pre_stg_incentives
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                           AS incentives_discount_value_lcy
    , '0'::NUMERIC                           AS incentives_promocode_value_lcy
    , '0'::NUMERIC                           AS incentives_cashback_amt
    , '0'::NUMERIC                           AS incentives_value_lcy
    , incentives_total_unallocated_value_rub AS incentives_from_finance_department_value_lcy
    , '0'::NUMERIC                           AS incentives_reserve_value_lcy
    , incentives_total_unallocated_value_rub AS incentives_final_w_reserve_value_lcy
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_incentives};
GRANT ALL ON {stg_incentives} TO "ed-avetisyan";
GRANT ALL ON {stg_incentives} TO agabitashvili;
GRANT ALL ON {stg_incentives} TO "robot-lavka-analyst";
