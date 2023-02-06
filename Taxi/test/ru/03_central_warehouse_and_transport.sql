/*============================================================
 Central Warehouse and Transport
============================================================*/
-- Определяем подмножество РЦ, чтобы далее вытащить операции, которые относятся только к РЦ
CREATE TEMPORARY TABLE cwh_dict
ON COMMIT DROP
AS (
  SELECT store_id
  FROM {stg_wms_store}
  WHERE source_name = '1c'
) DISTRIBUTED BY (store_id);
ANALYZE cwh_dict;

-- Выпиливаем расходные материалы, потому что у нас они учитываются штучно, а мы платим за перемещение коробок
CREATE TEMPORARY TABLE master_category_filtered
ON COMMIT DROP
AS (
  SELECT item_id
  FROM {master_category}
  WHERE COALESCE(lvl2_class_name, '') != 'Расходные материалы'
    AND COALESCE(lvl4_subcategory_name, '') NOT IN (
      'Упаковка для еды СП'
      , 'Упаковка для напитков СП'
    )
) DISTRIBUTED BY (item_id);
ANALYZE master_category_filtered;

-- Находим, сколько на каждую Лавку собрали товаров на каждом РЦ в конкретную дату
CREATE TEMPORARY TABLE store_dt_share
ON COMMIT DROP
AS (
  SELECT (i.utc_created_dttm AT TIME ZONE 'UTC'
                             AT TIME ZONE s.timezone_name)::DATE AS lcl_calculation_dt
    , s.country_name
    , s.city_name                                                AS region_name
    , i.store_id::VARCHAR                                        AS cwh_id   -- РЦ-отправитель
    , i.store_recipient_id::VARCHAR                              AS store_id -- Склад-получатель
    , date_trunc(
        'month', i.utc_created_dttm AT TIME ZONE 'UTC'
                                    AT TIME ZONE s.timezone_name
      )::DATE                                                    AS month_dt
    , SUM(i.item_cnt)                                            AS purchase_quantity
  FROM {item_in_warehouse} AS i
  JOIN {stg_wms_store} AS s
    ON i.store_recipient_id = s.store_id
  WHERE i.store_recipient_id IS NOT NULL
    AND i.document_type = 'РасходныйОрдерНаТовары'
    AND EXISTS (
      -- Вытаскиваем только такие операции, которые относятся к РЦ
      SELECT 1
      FROM cwh_dict AS d
      WHERE i.store_id = d.store_id
    )
    AND EXISTS (
      -- Исключаем расходные материалы
      SELECT 1
      FROM master_category_filtered AS mc
      WHERE i.item_id = mc.item_id
    )
    AND i.utc_created_dttm AT TIME ZONE 'UTC'
                           AT TIME ZONE s.timezone_name >= '2021-10-01 00:00:00'::TIMESTAMP
  GROUP BY 1, 2, 3, 4, 5, 6
) DISTRIBUTED BY (cwh_id, month_dt);
ANALYZE store_dt_share;

/*
 Справочник из Sharepoint'а для CWH.
 В нем обязательно должен быть текущий месяц. Если его вдруг не оказывается,
 то запись для текущего месяца искусственно создается из предыдущего
*/
CREATE TEMPORARY TABLE cwh_constant
ON COMMIT DROP
AS (
  -- 4. Если на текущий месяц выпала искусственная запись, то подменяем ей дату
  SELECT cwh_fixed_rate_lcy
    , cwh_id::VARCHAR
    , cwh_var_rate_lcy
    , CASE
        WHEN is_fake = TRUE
          THEN date_trunc('month', (now() AT TIME ZONE 'Europe/Moscow'))::DATE
        ELSE month_dt
      END               AS month_dt
    , region_name
    , utc_business_dttm
    , utc_created_dttm
    , utc_updated_dttm
    , is_fake           AS got_from_previous_month_flg
    , 'Россия'::VARCHAR AS country_name
  FROM
  (
    -- 3. Оставляем записи для предыдущего и более ранних месяцев, а также выбираем подходящую запись для текущего месяца
    SELECT *
    FROM (
      -- 2. Для каждого CWH задваиваем запись предпоследнего месяца + вычисляем максимальный месяц, имеющийся в таблице
      SELECT cwh.*
        , CASE
            WHEN fake.is_fake IS NULL
              THEN FALSE
            ELSE fake.is_fake
          END                                              AS is_fake
        , date_trunc(
            'month', (now() AT TIME ZONE 'Europe/Moscow')::TIMESTAMP - '1 month'::INTERVAL
          )::DATE                                          AS previous_month_from_now
        , MAX(cwh.month_dt) OVER (PARTITION BY cwh.cwh_id) AS maximal_month_at_table
      FROM {pnl_ru_cwh_constant} AS cwh
      LEFT JOIN (
        -- 1. Создаем ДВЕ записи с предпоследним месяцем - из одной будем делать текущий месяц
        SELECT *
        FROM (
          SELECT date_trunc(
                   'month', (now() AT TIME ZONE 'Europe/Moscow')::TIMESTAMP - '1 month'::INTERVAL
                 )::DATE AS month_dt
        ) AS prev_month
        CROSS JOIN (VALUES (TRUE), (FALSE)) AS tf(is_fake)
      ) AS fake
      ON cwh.month_dt = fake.month_dt
      WHERE cwh.month_dt <= (now() AT TIME ZONE 'Europe/Moscow')::DATE
    ) AS cwh
    WHERE     month_dt < previous_month_from_now
       OR     month_dt = previous_month_from_now AND is_fake = FALSE
       OR (   month_dt = previous_month_from_now AND is_fake = TRUE AND month_dt = maximal_month_at_table
           OR month_dt > previous_month_from_now AND month_dt = maximal_month_at_table
          )
  ) AS cwh
) DISTRIBUTED BY (cwh_id, month_dt);
ANALYZE cwh_constant;

/*
 Находим, сколько товаров собралось на данном РЦ за конкретный месяц;
 вдобавок, приджоиниваем константы из справочника
*/
CREATE TEMPORARY TABLE cwh_goods_qty
ON COMMIT DROP
AS (
  SELECT s.lcl_calculation_dt
    , s.country_name
    , s.region_name
    , s.store_id
    , s.month_dt
    , s.purchase_quantity
    , SUM(s.purchase_quantity) OVER w AS total_purchase_quantity
    , const.cwh_var_rate_lcy

    , CASE
        -- Если месяц уже закончился, то просто берем константу целиком
        WHEN s.month_dt < date_trunc('month', CURRENT_DATE - 1)::DATE
          THEN const.cwh_fixed_rate_lcy

        -- А для текущего месяца берем кусок от константы, пропорциональный количеству прошедших дней
        ELSE const.cwh_fixed_rate_lcy
               / EXTRACT(
                   DAYS FROM (s.month_dt + '1 month - 1 day'::INTERVAL)
                 )
               * EXTRACT(
                   DAYS FROM (CURRENT_DATE - 1)
                 )
      END                             AS cwh_fixed_rate_lcy

  FROM store_dt_share AS s
  JOIN cwh_constant AS const
    ON s.cwh_id = const.cwh_id
    AND s.month_dt = const.month_dt
    AND s.country_name = const.country_name
  WINDOW w AS (PARTITION BY s.cwh_id, s.month_dt, s.country_name)
) DISTRIBUTED BY (lcl_calculation_dt, country_name, region_name, store_id, month_dt);
ANALYZE cwh_goods_qty;

-- Вычисляем, сколько нужно заплатить складам
CREATE TEMPORARY TABLE cwh_shares
ON COMMIT DROP
AS (
  SELECT g.lcl_calculation_dt
    , g.country_name
    , g.region_name
    , g.store_id
    , g.month_dt

    -- Считаем, сколько суммарно нужно заплатить за все отгруженные в этот день товары на эту Лавку
    , SUM(
        COALESCE(
          g.cwh_var_rate_lcy * g.purchase_quantity, '0'::NUMERIC
        )
      )                                                                            AS cwh_var_value_lcy

    -- Размазываем константу пропроционально количеству собранных товаров на конкретную Лавку в конкретный день
    , SUM(
        COALESCE(
          g.cwh_fixed_rate_lcy * g.purchase_quantity / g.total_purchase_quantity, '0'::NUMERIC
        )
      )                                                                            AS cwh_fixed_value_lcy
  FROM cwh_goods_qty AS g
  JOIN {stg_store} AS stg
    ON g.store_id = stg.store_id
  WHERE stg.country_name IN ('Россия')
  GROUP BY 1, 2, 3, 4, 5
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE cwh_shares;

-- Обогащаем предыдущую таблицу так, чтобы данных хватило для расчета статей
CREATE TEMPORARY TABLE cwh_shares_enriched
ON COMMIT DROP
AS (
  SELECT s.lcl_calculation_dt
    , s.country_name
    , s.region_name
    , s.store_id
    , s.cwh_var_value_lcy
    , s.cwh_fixed_value_lcy
    , COALESCE(s.cwh_var_value_lcy, 0)
        + COALESCE(s.cwh_fixed_value_lcy, 0)          AS cwh_value_lcy
    , SUM(
        COALESCE(s.cwh_var_value_lcy, 0)
          + COALESCE(s.cwh_fixed_value_lcy, 0)
      ) OVER w                                        AS cwh_full_month_value_lcy
    , rv.cwh_total_reserve_value_lcy                  AS cwh_reserve_value_lcy
    , s.month_dt
  FROM cwh_shares AS s
  LEFT JOIN {stg_reserve} AS rv
    ON s.month_dt = rv.month_dt
    AND s.country_name = rv.country_name
  WINDOW w AS (PARTITION BY s.month_dt, s.country_name)
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE cwh_shares_enriched;

------------------------------
-- CWH
------------------------------
CREATE TEMPORARY TABLE pre_stg_cwh
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- Прогноз на основе cwh_constant (рассчитан уже в локальной валюте, поэтому переводить не нужно)
    , e.cwh_var_value_lcy::NUMERIC
    , e.cwh_fixed_value_lcy::NUMERIC
    , e.cwh_value_lcy::NUMERIC

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.cwh_fact_value_lcy
                 * e.cwh_value_lcy
                 / e.cwh_full_month_value_lcy
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS cwh_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.cwh_reserve_value_lcy IS NOT NULL
        AND e.cwh_reserve_value_lcy != 0
          THEN e.cwh_reserve_value_lcy
                 * e.cwh_value_lcy
                 / e.cwh_full_month_value_lcy
        ELSE 0.0
      END::NUMERIC                              AS cwh_reserve_value_lcy

    , mc.fiscal_year_closed_period_flg
  FROM cwh_shares_enriched AS e
  LEFT JOIN {stg_manual_correction} AS mc
    ON e.month_dt = mc.month_dt
    AND e.country_name = mc.country_name
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
  WHERE e.country_name IN ('Россия')
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_cwh;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_cwh}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , cwh_var_value_lcy
    , cwh_fixed_value_lcy
    , cwh_value_lcy
    , cwh_from_finance_department_value_lcy
    , cwh_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "прогноз + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN cwh_from_finance_department_value_lcy
        ELSE cwh_value_lcy + cwh_reserve_value_lcy
      END::NUMERIC                    AS cwh_final_w_reserve_value_lcy

  FROM pre_stg_cwh
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                    AS cwh_var_value_lcy
    , '0'::NUMERIC                    AS cwh_fixed_value_lcy
    , '0'::NUMERIC                    AS cwh_value_lcy
    , cwh_total_unallocated_value_rub AS cwh_from_finance_department_value_lcy
    , '0'::NUMERIC                    AS cwh_reserve_value_lcy
    , cwh_total_unallocated_value_rub AS cwh_final_w_reserve_value_lcy
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_cwh};
GRANT ALL ON {stg_cwh} TO "ed-avetisyan";
GRANT ALL ON {stg_cwh} TO agabitashvili;
GRANT ALL ON {stg_cwh} TO "robot-lavka-analyst";
