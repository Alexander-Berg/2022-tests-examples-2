/*==================================================
 Собираем инфу по свежеприбывшим курьерам
==================================================*/
-- Вытаскиваем новичков
CREATE TABLE {stg_new_courier}
AS (
  SELECT nc.lcl_calculation_dt
    , s.country_name
    , nc.region_name
    , nc.store_id
    , date_trunc('month', nc.lcl_calculation_dt)::DATE                                 AS month_dt
    , EXTRACT(
        DAYS FROM date_trunc('month', nc.lcl_calculation_dt) + '1 month - 1 day'::INTERVAL
      )                                                                                AS days_in_month
    , EXTRACT(
        DAYS FROM
          CASE WHEN date_trunc('month', nc.lcl_calculation_dt) = date_trunc('month', CURRENT_DATE - 1)
            THEN CURRENT_DATE - 1
            ELSE (date_trunc('month', nc.lcl_calculation_dt) + '1 month - 1 day'::INTERVAL)::DATE
          END
      )                                                                                AS days_in_month_passed
    , nc.new_courier_w_shift_start_and_completed_order_cnt                             AS new_courier_cnt
    , SUM(nc.new_courier_w_shift_start_and_completed_order_cnt) OVER w                 AS new_courier_full_month_cnt
  FROM {new_courier} AS nc
  JOIN {stg_store} AS s
    ON nc.store_id = s.store_id
  WHERE nc.lcl_calculation_dt >= '2021-10-01'::DATE
    AND s.country_name IN ('Россия')
  WINDOW w AS (PARTITION BY date_trunc('month', nc.lcl_calculation_dt), s.country_name)
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_new_courier};
GRANT ALL ON {stg_new_courier} TO "ed-avetisyan";
GRANT ALL ON {stg_new_courier} TO agabitashvili;
GRANT ALL ON {stg_new_courier} TO "robot-lavka-analyst";
