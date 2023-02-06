/*==================================================
 Собираем словарики городов и Лавок
==================================================*/
-- Вытаскиваем соответствие городов странам
CREATE TEMPORARY TABLE geo_hierarchy
ON COMMIT DROP
AS (
  SELECT DISTINCT tz_aggl_name_ru AS region_name
    , tz_country_name_ru          AS country_name
  FROM {geo_hierarchy}
) DISTRIBUTED BY (region_name);
ANALYZE geo_hierarchy;

-- Формируем wms.store со странами
DROP TABLE IF EXISTS {stg_wms_store};
CREATE TABLE {stg_wms_store}
AS (
  SELECT g.country_name
    , s.*
  FROM {ods_wms_store} AS s
  JOIN geo_hierarchy AS g
    ON s.city_name = g.region_name
) DISTRIBUTED BY (store_wms_id);
ANALYZE {stg_wms_store};
GRANT ALL ON {stg_wms_store} TO "ed-avetisyan";
GRANT ALL ON {stg_wms_store} TO agabitashvili;
GRANT ALL ON {stg_wms_store} TO "robot-lavka-analyst";

/*
Словарь Лавок:
 - Исключена вся международка, кроме Израиля
 - Исключена франшиза (Иркутск)
 - Лавкет не исключается
*/
DROP TABLE IF EXISTS {stg_store};
CREATE TABLE {stg_store}
AS (
  SELECT country_name
    , region_id
    , city_name AS region_name
    , store_id::VARCHAR
    , store_name::VARCHAR
  FROM {stg_wms_store}
  WHERE country_name IN ('Россия', 'Израиль')
    AND city_name NOT IN ('Иркутск')
) DISTRIBUTED BY (region_id);
ANALYZE {stg_store};
GRANT ALL ON {stg_store} TO "ed-avetisyan";
GRANT ALL ON {stg_store} TO agabitashvili;
GRANT ALL ON {stg_store} TO "robot-lavka-analyst";

-- Словарик с городами и странами
DROP TABLE IF EXISTS {stg_region_dict};
CREATE TABLE {stg_region_dict}
AS (
  SELECT DISTINCT country_name
    , region_id
    , region_name
  FROM {stg_store}
) DISTRIBUTED BY (region_name);
ANALYZE {stg_region_dict};
GRANT ALL ON {stg_region_dict} TO "ed-avetisyan";
GRANT ALL ON {stg_region_dict} TO agabitashvili;
GRANT ALL ON {stg_region_dict} TO "robot-lavka-analyst";

-- Замножаем список всех Лавок на каждую дату
DROP TABLE IF EXISTS {stg_stores_n_dates};
CREATE TABLE {stg_stores_n_dates}
AS (
  SELECT gs::DATE                         AS lcl_calculation_dt
    , s.country_name
    , s.region_id
    , s.region_name
    , s.store_id
    , s.store_name
    , date_trunc('month', gs::DATE)::DATE AS month_dt
  FROM (
    SELECT country_name
      , region_id
      , region_name
      , store_id
      , store_name::VARCHAR
    FROM {stg_store}
    UNION ALL
    -- В каждом городе создаем бутафорскую Лавку с id = 0,
    -- чтобы было куда списывать неаллоцируемые доходы и расходы
    SELECT country_name
      , region_id
      , region_name
      , '0'::VARCHAR
      , NULL::VARCHAR
    FROM {stg_region_dict}
  ) AS s
  CROSS JOIN generate_series('2021-10-01'::DATE, CURRENT_DATE - 1, '1 day'::INTERVAL) AS gs
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_stores_n_dates};
GRANT ALL ON {stg_stores_n_dates} TO "ed-avetisyan";
GRANT ALL ON {stg_stores_n_dates} TO agabitashvili;
GRANT ALL ON {stg_stores_n_dates} TO "robot-lavka-analyst";
