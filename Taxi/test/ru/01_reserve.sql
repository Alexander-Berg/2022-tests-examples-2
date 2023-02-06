/*==================================================
 Справочник с резервами из Sharepoint
==================================================*/
DROP TABLE IF EXISTS {stg_reserve};
CREATE TABLE {stg_reserve}
AS (
  SELECT *
    , 'Россия'::VARCHAR AS country_name
  FROM {pnl_ru_reserve}
) DISTRIBUTED BY (month_dt);
ANALYZE {stg_reserve};
GRANT ALL ON {stg_reserve} TO "ed-avetisyan";
GRANT ALL ON {stg_reserve} TO agabitashvili;
GRANT ALL ON {stg_reserve} TO "robot-lavka-analyst";
