/*============================================================
 COGS
============================================================*/
-- Тянем когсы из dm_lavka_order_item
CREATE TEMPORARY TABLE dmloi
ON COMMIT DROP
AS (
  SELECT i.lcl_created_dttm::DATE                                         AS lcl_calculation_dt
    , s.country_name
    , i.city_name                                                         AS region_name
    , i.store_id
    , date_trunc('month', i.lcl_created_dttm)::DATE                       AS month_dt
    , SUM(i.item_purchase_cost_wo_vat_rub * i.item_cnt / i.currency_rate) AS cogs_value_lcy
  FROM {dm_lavka_order_item} AS i
  JOIN {stg_store} AS s
    ON i.store_id = s.store_id
  WHERE i.lcl_created_dttm >= '2021-10-01 00:00:00'::TIMESTAMP
    AND i.order_status = 'complete'
    AND s.country_name IN ('Россия', 'Израиль')
  GROUP BY 1, 2, 3, 4, 5
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE dmloi;

-- Обогащаем предыдущую таблицу так, чтобы данных хватило для расчета статей
CREATE TEMPORARY TABLE dmloi_enriched
ON COMMIT DROP
AS (
  SELECT d.lcl_calculation_dt
    , d.country_name
    , d.region_name
    , d.store_id
    , d.month_dt
    , d.cogs_value_lcy
    , d.cogs_value_lcy * gc.cogs_reserve_shr AS cogs_permanent_reserve_value_lcy
    , SUM(d.cogs_value_lcy) OVER w           AS cogs_full_month_value_lcy
    , rv.cogs_reserve_value_lcy
  FROM dmloi AS d
  LEFT JOIN {stg_general_constant} AS gc
    ON d.month_dt = gc.month_dt
    AND d.country_name = gc.country_name
  LEFT JOIN {stg_reserve} AS rv
    ON d.month_dt = rv.month_dt
    AND d.country_name = rv.country_name
  WINDOW w AS (PARTITION BY d.month_dt, d.country_name)
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE dmloi_enriched;

------------------------------
-- COGS
------------------------------
CREATE TEMPORARY TABLE pre_stg_cogs
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- Факт из источника (приходит уже в локальной валюте, поэтому переводить не нужно)
    , e.cogs_value_lcy::NUMERIC                 AS cogs_value_lcy

    -- Перманентный резерв (рассчитан на основе факта, поэтому он тоже сразу в локальной валюте)
    , e.cogs_permanent_reserve_value_lcy::NUMERIC

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.cogs_fact_value_lcy
                 * e.cogs_value_lcy
                 / e.cogs_full_month_value_lcy
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS cogs_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.cogs_reserve_value_lcy IS NOT NULL
        AND e.cogs_reserve_value_lcy != 0
          THEN e.cogs_reserve_value_lcy
                 * e.cogs_value_lcy
                 / e.cogs_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS cogs_reserve_value_lcy

    , mc.fiscal_year_closed_period_flg
  FROM dmloi_enriched AS e
  LEFT JOIN {stg_manual_correction} AS mc
    ON e.month_dt = mc.month_dt
    AND e.country_name = mc.country_name
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_cogs;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_cogs}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , cogs_value_lcy
    , cogs_permanent_reserve_value_lcy
    , cogs_from_finance_department_value_lcy
    , cogs_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "факт + перманентный резерв + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN cogs_from_finance_department_value_lcy
        ELSE cogs_value_lcy + cogs_permanent_reserve_value_lcy + cogs_reserve_value_lcy
      END::NUMERIC               AS cogs_final_w_reserve_value_lcy

  FROM pre_stg_cogs
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC               AS cogs_value_lcy
    , '0'::NUMERIC               AS cogs_permanent_reserve_value_lcy
    , cogs_unallocated_value_rub AS cogs_from_finance_department_value_lcy
    , '0'::NUMERIC               AS cogs_reserve_value_lcy
    , cogs_unallocated_value_rub AS cogs_final_w_reserve_value_lcy
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_cogs};
GRANT ALL ON {stg_cogs} TO "ed-avetisyan";
GRANT ALL ON {stg_cogs} TO agabitashvili;
GRANT ALL ON {stg_cogs} TO "robot-lavka-analyst";
