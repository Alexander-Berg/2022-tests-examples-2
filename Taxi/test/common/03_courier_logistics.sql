/*============================================================
 Courier Logistics
============================================================*/
-- Вытаскиваем подходящие записи из CPO
CREATE TEMPORARY TABLE cpo_united
ON COMMIT DROP
AS (
  SELECT sd.country_name
    , sd.month_dt
    , cpo.*
  FROM (
    SELECT "date"                        AS lcl_calculation_dt
      , region_name
      , COALESCE(place_id, '0')::VARCHAR AS store_id
      , "cost"
    FROM {cpo}
    WHERE "date" >= '2021-10-01'::DATE
      AND component NOT IN (
        'additional_compensation_manual_amount'            -- Рефералка, реактиваци и т.д.
        , 'tips'                                           -- Чаевые курьерам
      )
    UNION ALL
    SELECT "date"                        AS lcl_calculation_dt
      , region_name
      , COALESCE(place_id, '0')::VARCHAR AS store_id
      , "cost"
    FROM {cpo_old}
    WHERE "date" >= '2021-10-01'::DATE
      AND component NOT IN (
        'additional_compensation_manual_amount_weighted'   -- Тоже рефералка, но в предыдущей версии
        , 'tips'                                           -- Чаевые курьерам
      )
  ) AS cpo
  JOIN {stg_stores_n_dates} AS sd
    ON cpo.lcl_calculation_dt = sd.lcl_calculation_dt
    AND cpo.store_id = sd.store_id
    AND cpo.region_name = sd.region_name
  WHERE sd.country_name IN ('Россия', 'Израиль')
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE cpo_united;

-- Схлопываем записи до разреза "День + Лавка"
CREATE TEMPORARY TABLE cpo_grouped
ON COMMIT DROP
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , month_dt
    , SUM("cost") AS courier_logistics_value_lcy
  FROM cpo_united
  GROUP BY 1, 2, 3, 4, 5
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE cpo_grouped;

/*
Courier Logistics - это (вроде бы) единственная статья, в которой фиктивная нулевая Лавка
может прилетать еще и из факта из источника, а не только из неаллоцированного финансового итога.
Поэтому, при разывании финансового итога из manual_corrections важно убедиться,
что CPO'шные нулевые Лавки в этом не участвуют.

Сами же нулевые Лавки мы откладываем куда-нибудь в отдельное место. А затем, когда итог будет размазан,
мы вернем их обратно в общую кучу. При этом, записи для нулевых Лавок
мы обогатим неаллоцированным финансовым итогом
*/
-- Складываем факт по нулевым Лавкам в отдельную таблицу
CREATE TEMPORARY TABLE cpo_grouped_zeroth_store_only
ON COMMIT DROP
AS (
  SELECT *
  FROM cpo_grouped
  WHERE store_id = '0'::VARCHAR
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE cpo_grouped_zeroth_store_only;

-- Обогащаем данные по ненулевым Лавкам так, чтобы данных хватило для расчета статьи
CREATE TEMPORARY TABLE cpo_grouped_enriched
ON COMMIT DROP
AS (
  SELECT cpo.lcl_calculation_dt
    , cpo.country_name
    , cpo.region_name
    , cpo.store_id
    , cpo.month_dt
    , cpo.courier_logistics_value_lcy
    , SUM(cpo.courier_logistics_value_lcy) OVER w AS courier_logistics_full_month_value_lcy
    , rv.courier_logistics_reserve_value_lcy
  FROM cpo_grouped AS cpo
  LEFT JOIN {stg_reserve} AS rv
    ON cpo.month_dt = rv.month_dt
    AND cpo.country_name = rv.country_name
  WHERE cpo.store_id != '0'::VARCHAR
  WINDOW w AS (PARTITION BY cpo.month_dt, cpo.country_name)
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE cpo_grouped_enriched;

------------------------------
-- Courier Logistics
------------------------------
CREATE TEMPORARY TABLE pre_stg_courier_logistics
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- Факт из источника (приходит уже в локальной валюте, поэтому переводить не нужно)
    , e.courier_logistics_value_lcy::NUMERIC    AS courier_logistics_value_lcy

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.courier_logistics_w_easy_logistics_fact_value_lcy
                 * e.courier_logistics_value_lcy
                 / e.courier_logistics_full_month_value_lcy
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS courier_logistics_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.courier_logistics_reserve_value_lcy IS NOT NULL
        AND e.courier_logistics_reserve_value_lcy != 0
          THEN e.courier_logistics_reserve_value_lcy
                 * e.courier_logistics_value_lcy
                 / e.courier_logistics_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS courier_logistics_reserve_value_lcy

    , mc.fiscal_year_closed_period_flg
  FROM cpo_grouped_enriched AS e
  LEFT JOIN {stg_manual_correction} AS mc
    ON e.month_dt = mc.month_dt
    AND e.country_name = mc.country_name
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_courier_logistics;

-- Разбираемся с нулевой Лавкой: соединяем факт и неаллоцированные деньги от финансистов
CREATE TEMPORARY TABLE pre_stg_courier_logistics_unallocated
ON COMMIT DROP
AS (
  SELECT COALESCE(u.lcl_calculation_dt, g.lcl_calculation_dt) AS lcl_calculation_dt
    , date_trunc(
        'month', COALESCE(
          u.lcl_calculation_dt, g.lcl_calculation_dt
        )
      )::DATE                                                 AS month_dt
    , COALESCE(u.country_name, g.country_name)                AS country_name
    , COALESCE(u.region_name, g.region_name)                  AS region_name
    , COALESCE(u.store_id, g.store_id)                        AS store_id
    , COALESCE(g.courier_logistics_value_lcy, 0)::NUMERIC     AS courier_logistics_value_lcy
    , COALESCE(
        u.courier_logistics_unallocated_value_rub, 0
      )::NUMERIC                                              AS courier_logistics_from_finance_department_value_lcy
  FROM {stg_unallocated_by_days} AS u
  FULL JOIN cpo_grouped_zeroth_store_only AS g
    ON u.lcl_calculation_dt = g.lcl_calculation_dt
    AND u.region_name = g.region_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_courier_logistics_unallocated;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_courier_logistics}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , courier_logistics_value_lcy
    , courier_logistics_from_finance_department_value_lcy
    , courier_logistics_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "факт + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN courier_logistics_from_finance_department_value_lcy
        ELSE courier_logistics_value_lcy + courier_logistics_reserve_value_lcy
      END::NUMERIC                            AS courier_logistics_final_w_reserve_value_lcy

  FROM pre_stg_courier_logistics
  UNION ALL
  SELECT u.lcl_calculation_dt
    , u.country_name
    , u.region_name
    , u.store_id
    , u.courier_logistics_value_lcy
    , u.courier_logistics_from_finance_department_value_lcy
    , '0'::NUMERIC                            AS courier_logistics_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то факт из источника
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN u.courier_logistics_from_finance_department_value_lcy
        ELSE u.courier_logistics_value_lcy
      END::NUMERIC                            AS courier_logistics_final_w_reserve_value_lcy

  FROM pre_stg_courier_logistics_unallocated AS u
  LEFT JOIN {stg_manual_correction} AS mc
    ON u.month_dt = mc.month_dt
    AND u.country_name = mc.country_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_courier_logistics};
GRANT ALL ON {stg_courier_logistics} TO "ed-avetisyan";
GRANT ALL ON {stg_courier_logistics} TO agabitashvili;
GRANT ALL ON {stg_courier_logistics} TO "robot-lavka-analyst";
