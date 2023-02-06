------------------------------
-- Utilities
------------------------------
CREATE TEMPORARY TABLE pre_stg_utilities
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- План (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , COALESCE(e.utilities_plan_value_lcy, 0)
        / cr.lcl_to_rub::NUMERIC                AS utilities_value_lcy

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , COALESCE(e.utilities_fact_value_lcy, 0)
        / cr.lcl_to_rub::NUMERIC                AS utilities_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.utilities_reserve_value_lcy IS NOT NULL
        AND e.utilities_reserve_value_lcy != 0
          THEN e.utilities_reserve_value_lcy
                 * e.utilities_plan_value_lcy
                 / e.utilities_plan_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS utilities_reserve_value_lcy

    , e.utilities_plan_value_lcy
    , e.utilities_fact_value_lcy
    , e.utilities_plan_method_name

  FROM {stg_mc_by_place_enriched} AS e
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
  WHERE e.country_name IN ('Россия')
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_utilities;

-- Формируем умное поле + добавляем неаллоцированные деньги
DROP TABLE IF EXISTS {stg_utilities};
CREATE TABLE {stg_utilities}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , utilities_value_lcy
    , utilities_from_finance_department_value_lcy
    , utilities_reserve_value_lcy

    -- Умное поле: если есть финансовый итог, то берем его, а если нет, то берем связку "план + резерв"
    , COALESCE(
        utilities_fact_value_lcy,
        utilities_plan_value_lcy + utilities_reserve_value_lcy
      )::NUMERIC   AS utilities_final_w_reserve_value_lcy

    -- Текстовка с методологией
    , CASE
        WHEN utilities_fact_value_lcy IS NOT NULL
          THEN '{txt_financial_total_sp}'
        ELSE utilities_plan_value_lcy
      END::VARCHAR AS utilities_final_method_name

  FROM pre_stg_utilities
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                        AS utilities_value_lcy
    , utilities_unallocated_value_rub     AS utilities_from_finance_department_value_lcy
    , '0'::NUMERIC                        AS utilities_reserve_value_lcy
    , utilities_unallocated_value_rub     AS utilities_final_w_reserve_value_lcy
    , '{txt_financial_total_sp}'::VARCHAR AS utilities_final_method_name
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_utilities};
GRANT ALL ON {stg_utilities} TO "ed-avetisyan";
GRANT ALL ON {stg_utilities} TO agabitashvili;
GRANT ALL ON {stg_utilities} TO "robot-lavka-analyst";
