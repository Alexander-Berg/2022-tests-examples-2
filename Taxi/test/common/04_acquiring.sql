------------------------------
-- Acquiring
------------------------------
CREATE TEMPORARY TABLE pre_stg_acquiring
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- Прогноз на основе general_constant (рассчитан уже в локальной валюте, поэтому переводить не нужно)
    , e.acquiring_value_lcy::NUMERIC            AS acquiring_value_lcy

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.acquiring_fact_value_lcy
                 * e.acquiring_value_lcy
                 / e.acquiring_full_month_value_lcy
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS acquiring_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.acquiring_reserve_value_lcy IS NOT NULL
        AND e.acquiring_reserve_value_lcy != 0
          THEN e.acquiring_reserve_value_lcy
                 * e.acquiring_value_lcy
                 / e.acquiring_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS acquiring_reserve_value_lcy

    , mc.fiscal_year_closed_period_flg
  FROM {stg_agg_pnl_enriched} AS e
  LEFT JOIN {stg_manual_correction} AS mc
    ON e.month_dt = mc.month_dt
    AND e.country_name = mc.country_name
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
  WHERE e.country_name IN ('Россия', 'Израиль')
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_acquiring;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_acquiring}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , acquiring_value_lcy
    , acquiring_from_finance_department_value_lcy
    , acquiring_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "прогноз + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN acquiring_from_finance_department_value_lcy
        ELSE acquiring_value_lcy + acquiring_reserve_value_lcy
      END::NUMERIC                    AS acquiring_final_w_reserve_value_lcy

  FROM pre_stg_acquiring
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                    AS acquiring_value_lcy
    , acquiring_unallocated_value_rub AS acquiring_from_finance_department_value_lcy
    , '0'::NUMERIC                    AS acquiring_reserve_value_lcy
    , acquiring_unallocated_value_rub AS acquiring_final_w_reserve_value_lcy
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_acquiring};
GRANT ALL ON {stg_acquiring} TO "ed-avetisyan";
GRANT ALL ON {stg_acquiring} TO agabitashvili;
GRANT ALL ON {stg_acquiring} TO "robot-lavka-analyst";
