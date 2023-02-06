------------------------------
-- Insurance and SMS
------------------------------
CREATE TEMPORARY TABLE pre_stg_insurance_and_sms
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- Факт из источника (приходит уже в локальной валюте, поэтому переводить не нужно)
    , e.insurance_and_sms_value_lcy::NUMERIC    AS insurance_and_sms_value_lcy

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.insurance_and_sms_fact_value_lcy
                 * e.insurance_and_sms_value_lcy
                 / e.insurance_and_sms_full_month_value_lcy
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS insurance_and_sms_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.insurance_reserve_value_lcy IS NOT NULL
        AND e.insurance_reserve_value_lcy != 0
          THEN e.insurance_reserve_value_lcy
                 * e.insurance_and_sms_value_lcy
                 / e.insurance_and_sms_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS insurance_reserve_value_lcy
    , CASE
        WHEN e.sms_reserve_value_lcy IS NOT NULL
        AND e.sms_reserve_value_lcy != 0
          THEN e.sms_reserve_value_lcy
                 * e.insurance_and_sms_value_lcy
                 / e.insurance_and_sms_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS sms_reserve_value_lcy
    , CASE
        WHEN e.insurance_reserve_value_lcy IS NOT NULL
        AND e.insurance_reserve_value_lcy != 0
          THEN e.insurance_reserve_value_lcy
                 * e.insurance_and_sms_value_lcy
                 / e.insurance_and_sms_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC
        + CASE
            WHEN e.sms_reserve_value_lcy IS NOT NULL
            AND e.sms_reserve_value_lcy != 0
              THEN e.sms_reserve_value_lcy
                     * e.insurance_and_sms_value_lcy
                     / e.insurance_and_sms_full_month_value_lcy
            ELSE 0.0
          END::NUMERIC                          AS insurance_and_sms_reserve_value_lcy

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
ANALYZE pre_stg_insurance_and_sms;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_insurance_and_sms}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , insurance_and_sms_value_lcy
    , insurance_and_sms_from_finance_department_value_lcy
    , insurance_reserve_value_lcy
    , sms_reserve_value_lcy
    , insurance_and_sms_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "факт + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN insurance_and_sms_from_finance_department_value_lcy
        ELSE insurance_and_sms_value_lcy + insurance_and_sms_reserve_value_lcy
      END::NUMERIC                                                AS insurance_and_sms_final_w_reserve_value_lcy

  FROM pre_stg_insurance_and_sms
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                                                AS insurance_and_sms_value_lcy
    , insurance_unallocated_value_rub + sms_unallocated_value_rub AS insurance_and_sms_from_finance_department_value_lcy
    , '0'::NUMERIC                                                AS insurance_reserve_value_lcy
    , '0'::NUMERIC                                                AS sms_reserve_value_lcy
    , '0'::NUMERIC                                                AS insurance_and_sms_reserve_value_lcy
    , insurance_unallocated_value_rub + sms_unallocated_value_rub AS insurance_and_sms_final_w_reserve_value_lcy
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_insurance_and_sms};
GRANT ALL ON {stg_insurance_and_sms} TO "ed-avetisyan";
GRANT ALL ON {stg_insurance_and_sms} TO agabitashvili;
GRANT ALL ON {stg_insurance_and_sms} TO "robot-lavka-analyst";
