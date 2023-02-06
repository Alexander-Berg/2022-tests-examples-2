/*============================================================
 Writeoffs
============================================================*/
-- Тянем списания
CREATE TEMPORARY TABLE writeoff_recount
ON COMMIT DROP
AS (
  SELECT w.lcl_dt                         AS lcl_calculation_dt
    , s.country_name
    , w.city_name                         AS region_name
    , w.store_id
    , date_trunc('month', w.lcl_dt)::DATE AS month_dt
    , SUM(w.item_cost_wo_vat_lcy)         AS writeoffs_value_lcy
  FROM {writeoff_recount} AS w
  JOIN {stg_store} AS s
    ON w.store_id = s.store_id
  WHERE w.lcl_dt >= '2021-10-01'::DATE
    AND w.reason_level_1_ru = 'Списания'
    AND s.country_name IN ('Россия', 'Израиль')
  GROUP BY 1, 2, 3, 4, 5
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE writeoff_recount;

-- Обогащаем предыдущую таблицу так, чтобы данных хватило для расчета статей
CREATE TEMPORARY TABLE writeoff_recount_enriched
ON COMMIT DROP
AS (
  SELECT wr.lcl_calculation_dt
    , wr.country_name
    , wr.region_name
    , wr.store_id
    , wr.month_dt
    , wr.writeoffs_value_lcy
    , wr.writeoffs_value_lcy * gc.writeoffs_reserve_shr AS writeoffs_permanent_reserve_value_lcy
    , SUM(wr.writeoffs_value_lcy) OVER w                AS writeoffs_full_month_value_lcy
    , rv.writeoffs_reserve_value_lcy
  FROM writeoff_recount AS wr
  LEFT JOIN {stg_general_constant} AS gc
    ON wr.month_dt = gc.month_dt
    AND wr.country_name = gc.country_name
  LEFT JOIN {stg_reserve} AS rv
    ON wr.month_dt = rv.month_dt
    AND wr.country_name = rv.country_name
  WINDOW w AS (PARTITION BY wr.month_dt, wr.country_name)
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE writeoff_recount_enriched;

------------------------------
-- Writeoffs
------------------------------
CREATE TEMPORARY TABLE pre_stg_writeoffs
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- Факт из источника (приходит уже в локальной валюте, поэтому переводить не нужно)
    , e.writeoffs_value_lcy::NUMERIC            AS writeoffs_value_lcy

    -- Перманентный резерв (рассчитан на основе факта, поэтому он тоже сразу в локальной валюте)
    , e.writeoffs_permanent_reserve_value_lcy::NUMERIC

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.writeoffs_fact_value_lcy
                 * e.writeoffs_value_lcy
                 / e.writeoffs_full_month_value_lcy
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS writeoffs_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.writeoffs_reserve_value_lcy IS NOT NULL
        AND e.writeoffs_reserve_value_lcy != 0
          THEN e.writeoffs_reserve_value_lcy
                 * e.writeoffs_value_lcy
                 / e.writeoffs_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS writeoffs_reserve_value_lcy

    , mc.fiscal_year_closed_period_flg
  FROM writeoff_recount_enriched AS e
  LEFT JOIN {stg_manual_correction} AS mc
    ON e.month_dt = mc.month_dt
    AND e.country_name = mc.country_name
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_writeoffs;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_writeoffs}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , writeoffs_value_lcy
    , writeoffs_permanent_reserve_value_lcy
    , writeoffs_from_finance_department_value_lcy
    , writeoffs_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "факт + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN writeoffs_from_finance_department_value_lcy
        ELSE writeoffs_value_lcy + writeoffs_reserve_value_lcy
      END::NUMERIC                    AS writeoffs_final_w_reserve_value_lcy

  FROM pre_stg_writeoffs
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                    AS writeoffs_value_lcy
    , '0'::NUMERIC                    AS writeoffs_permanent_reserve_value_lcy
    , writeoffs_unallocated_value_rub AS writeoffs_from_finance_department_value_lcy
    , '0'::NUMERIC                    AS writeoffs_reserve_value_lcy
    , writeoffs_unallocated_value_rub AS writeoffs_final_w_reserve_value_lcy
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_writeoffs};
GRANT ALL ON {stg_writeoffs} TO "ed-avetisyan";
GRANT ALL ON {stg_writeoffs} TO agabitashvili;
GRANT ALL ON {stg_writeoffs} TO "robot-lavka-analyst";
