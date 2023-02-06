/*=====================================================================================
 В справочнике обязательно должен быть текущий месяц. Если его вдруг не оказывается,
 то запись для текущего месяца искусственно создается из предыдущего
=====================================================================================*/
CREATE TEMPORARY TABLE ru_general_constant
  ON COMMIT DROP AS (
  -- 4. Если на текущий месяц выпала искусственная запись, то подменяем ей дату
  SELECT acquiring_per_gmv_less_incentives_shr
    , brand_royalty_per_gmv_shr
    , cogs_reserve_shr
    , writeoffs_reserve_shr
    , courier_acquisition_per_order_lcy
    , insurance_and_sms_per_order_lcy
    , last_mile_revenue_per_item_lcy
    , CASE
        WHEN is_fake = TRUE
          THEN date_trunc('month', (now() AT TIME ZONE 'Europe/Moscow'))::DATE
        ELSE month_dt
      END                           AS month_dt
    , other_logistics_per_order_lcy
    , packaging_per_order_lcy
    , support_per_order_lcy
    , transport_per_order_lcy
    , utc_business_dttm
    , utc_created_dttm
    , utc_updated_dttm
    , is_fake                       AS got_from_previous_month_flg
    , 'Россия'::VARCHAR             AS country_name
  FROM
  (
    -- 3. Оставляем записи для предыдущего и более ранних месяцев, а также выбираем подходящую запись для текущего месяца
    SELECT *
    FROM (
      -- 2. Задваиваем запись предпоследнего месяца + вычисляем максимальный месяц, имеющийся в таблице
      SELECT gc.*
        , CASE
            WHEN fake.is_fake IS NULL
              THEN FALSE
            ELSE fake.is_fake
          END                      AS is_fake
        , date_trunc(
            'month', (now() AT TIME ZONE 'Europe/Moscow') - '1 month'::INTERVAL
          )::DATE                  AS previous_month_from_now
        , MAX(gc.month_dt) OVER () AS maximal_month_at_table
      FROM {pnl_ru_general_constant} AS gc
      LEFT JOIN (
        -- 1. Создаем ДВЕ записи с предпоследним месяцем - из одной будем делать текущий месяц
        SELECT *
        FROM (
          SELECT date_trunc(
                   'month', (now() AT TIME ZONE 'Europe/Moscow') - '1 month'::INTERVAL
                 )::DATE AS month_dt
        ) prev_month
        CROSS JOIN (VALUES (TRUE), (FALSE)) AS tf(is_fake)
      ) AS fake
      ON gc.month_dt = fake.month_dt
      WHERE gc.month_dt <= (now() AT TIME ZONE 'Europe/Moscow')::DATE
    ) AS gc
    WHERE     month_dt < previous_month_from_now
       OR     month_dt = previous_month_from_now AND is_fake = FALSE
       OR (   month_dt = previous_month_from_now AND is_fake = TRUE AND month_dt = maximal_month_at_table
           OR month_dt > previous_month_from_now AND month_dt = maximal_month_at_table
          )
  ) AS gc
) DISTRIBUTED BY (month_dt);
ANALYZE ru_general_constant;

CREATE TEMPORARY TABLE il_general_constant
 ON COMMIT DROP AS (
    -- 4. Если на текущий месяц выпала искусственная запись, то подменяем ей дату
  SELECT acquiring_per_gmv_less_incentives_shr
    , NULL::NUMERIC                 AS brand_royalty_per_gmv_shr
    , cogs_permanent_reserve_shr
    , writeoffs_permanent_reserve_shr
    , NULL::NUMERIC                 AS courier_acquisition_per_order_lcy
    , NULL::NUMERIC                 AS insurance_and_sms_per_order_lcy
    , NULL::NUMERIC                 AS last_mile_revenue_per_item_lcy
    , CASE
        WHEN is_fake = TRUE
          THEN date_trunc('month', (now() AT TIME ZONE 'Europe/Moscow'))::DATE
        ELSE month_dt
      END                           AS month_dt
    , NULL::NUMERIC                 AS other_logistics_per_order_lcy
    , packaging_per_order_value_lcy AS packaging_per_order_lcy
    , NULL::NUMERIC                 AS support_per_order_lcy
    , NULL::NUMERIC                 AS transport_per_order_lcy
    , utc_business_dttm
    , utc_created_dttm
    , utc_updated_dttm
    , is_fake                       AS got_from_previous_month_flg
    , 'Израиль'::VARCHAR            AS country_name
  FROM
  (
    -- 3. Оставляем записи для предыдущего и более ранних месяцев, а также выбираем подходящую запись для текущего месяца
    SELECT *
    FROM (
      -- 2. Задваиваем запись предпоследнего месяца + вычисляем максимальный месяц, имеющийся в таблице
      SELECT gc.*
        , CASE
            WHEN fake.is_fake IS NULL
              THEN FALSE
            ELSE fake.is_fake
          END                      AS is_fake
        , date_trunc(
            'month', (now() AT TIME ZONE 'Europe/Moscow') - '1 month'::INTERVAL
          )::DATE                  AS previous_month_from_now
        , MAX(gc.month_dt) OVER () AS maximal_month_at_table
      FROM {pnl_il_general_constant} AS gc
      LEFT JOIN (
        -- 1. Создаем ДВЕ записи с предпоследним месяцем - из одной будем делать текущий месяц
        SELECT *
        FROM (
          SELECT date_trunc(
                   'month', (now() AT TIME ZONE 'Europe/Moscow') - '1 month'::INTERVAL
                 )::DATE AS month_dt
        ) prev_month
        CROSS JOIN (VALUES (TRUE), (FALSE)) AS tf(is_fake)
      ) AS fake
      ON gc.month_dt = fake.month_dt
      WHERE gc.month_dt <= (now() AT TIME ZONE 'Europe/Moscow')::DATE
    ) AS gc
    WHERE     month_dt < previous_month_from_now
       OR     month_dt = previous_month_from_now AND is_fake = FALSE
       OR (   month_dt = previous_month_from_now AND is_fake = TRUE AND month_dt = maximal_month_at_table
           OR month_dt > previous_month_from_now AND month_dt = maximal_month_at_table
          )
  ) AS gc
) DISTRIBUTED BY (month_dt);
ANALYZE il_general_constant;


DROP TABLE IF EXISTS {stg_general_constant};
CREATE TABLE {stg_general_constant}
AS (
  SELECT *
  FROM ru_general_constant
  UNION ALL
  SELECT *
  FROM il_general_constant
) DISTRIBUTED BY (month_dt);
ANALYZE {stg_general_constant};
GRANT ALL ON {stg_general_constant} TO "ed-avetisyan";
GRANT ALL ON {stg_general_constant} TO agabitashvili;
GRANT ALL ON {stg_general_constant} TO "robot-lavka-analyst";
