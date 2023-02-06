------------------------------
-- Rents
------------------------------
CREATE TEMPORARY TABLE pre_stg_rents
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- План (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , COALESCE(e.rent_plan_value_lcy, 0)
        / cr.lcl_to_rub::NUMERIC                AS rents_value_lcy

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , COALESCE(e.rent_fact_value_lcy, 0)
        / cr.lcl_to_rub::NUMERIC                AS rents_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.rent_reserve_value_lcy IS NOT NULL
        AND e.rent_reserve_value_lcy != 0
          THEN e.rent_reserve_value_lcy
                 * e.rent_plan_value_lcy
                 / e.rent_plan_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS rents_reserve_value_lcy

    , e.rent_plan_value_lcy
    , e.rent_fact_value_lcy
    , e.rent_plan_method_name

  FROM {stg_mc_by_place_enriched} AS e
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
  WHERE e.country_name IN ('Россия')
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_rents;

-- Формируем умное поле + добавляем неаллоцированные деньги
DROP TABLE IF EXISTS {stg_rents};
CREATE TABLE {stg_rents}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , rents_value_lcy
    , rents_from_finance_department_value_lcy
    , rents_reserve_value_lcy

    -- Умное поле: если есть финансовый итог, то берем его, а если нет, то берем связку "план + резерв"
    , COALESCE(
        rent_fact_value_lcy,
        rent_plan_value_lcy + rents_reserve_value_lcy
      )::NUMERIC   AS rents_final_w_reserve_value_lcy

    -- Текстовка с методологией
    , CASE
        WHEN rent_fact_value_lcy IS NOT NULL
          THEN '{txt_financial_total_sp}'
        ELSE rent_plan_method_name
      END::VARCHAR AS rents_final_method_name

  FROM pre_stg_rents
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                        AS rents_value_lcy
    , rent_unallocated_value_rub          AS rents_from_finance_department_value_lcy
    , '0'::NUMERIC                        AS rents_reserve_value_lcy
    , rent_unallocated_value_rub          AS rents_final_w_reserve_value_lcy
    , '{txt_financial_total_sp}'::VARCHAR AS rents_final_method_name
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_rents};
GRANT ALL ON {stg_rents} TO "ed-avetisyan";
GRANT ALL ON {stg_rents} TO agabitashvili;
GRANT ALL ON {stg_rents} TO "robot-lavka-analyst";
