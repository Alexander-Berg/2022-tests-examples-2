------------------------------
-- People Cost
------------------------------
CREATE TEMPORARY TABLE pre_stg_people_cost
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- План (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , COALESCE(e.people_cost_plan_lcy, 0)
        / cr.lcl_to_rub::NUMERIC                AS people_cost_value_lcy

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , COALESCE(e.people_cost_fact_lcy, 0)
        / cr.lcl_to_rub::NUMERIC                AS people_cost_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.people_cost_reserve_value_lcy IS NOT NULL
        AND e.people_cost_reserve_value_lcy != 0
          THEN e.people_cost_reserve_value_lcy
                 * e.people_cost_plan_lcy
                 / e.people_cost_plan_full_month_lcy
        ELSE 0.0
      END::NUMERIC                              AS people_cost_reserve_value_lcy

    , e.people_cost_plan_lcy
    , e.people_cost_fact_lcy
    , e.people_cost_plan_method_name

  FROM {stg_mc_by_place_enriched} AS e
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
  WHERE e.country_name IN ('Россия')
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_people_cost;

-- Формируем умное поле + добавляем неаллоцированные деньги
DROP TABLE IF EXISTS {stg_people_cost};
CREATE TABLE {stg_people_cost}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , people_cost_value_lcy
    , people_cost_from_finance_department_value_lcy
    , people_cost_reserve_value_lcy

    -- Умное поле: если есть финансовый итог, то берем его, а если нет, то берем связку "план + резерв"
    , COALESCE(
        people_cost_fact_lcy,
        people_cost_plan_lcy + people_cost_reserve_value_lcy
      )::NUMERIC   AS people_cost_final_w_reserve_value_lcy

    -- Текстовка с методологией
    , CASE
        WHEN people_cost_fact_lcy IS NOT NULL
          THEN '{txt_financial_total_sp}'
        ELSE people_cost_plan_lcy
      END::VARCHAR AS people_cost_final_method_name

  FROM pre_stg_people_cost
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                        AS people_cost_value_lcy
    , people_cost_unallocated_value_rub   AS people_cost_from_finance_department_value_lcy
    , '0'::NUMERIC                        AS people_cost_reserve_value_lcy
    , people_cost_unallocated_value_rub   AS people_cost_final_w_reserve_value_lcy
    , '{txt_financial_total_sp}'::VARCHAR AS people_cost_final_method_name
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_people_cost};
GRANT ALL ON {stg_people_cost} TO "ed-avetisyan";
GRANT ALL ON {stg_people_cost} TO agabitashvili;
GRANT ALL ON {stg_people_cost} TO "robot-lavka-analyst";
