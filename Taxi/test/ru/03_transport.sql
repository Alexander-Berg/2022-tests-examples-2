/*============================================================
-- Transport
============================================================*/
-- Вытаскиваем заказы с велосипедами
CREATE TEMPORARY TABLE bike_orders
ON COMMIT DROP AS (
  SELECT dmlo.local_created_dttm::DATE                                          AS lcl_calculation_dt
    , date_trunc('month', dmlo.local_created_dttm)                              AS month_dt
    , dmlo.place_id::VARCHAR                                                    AS store_id
    , dmlo.country_name
    , dmlo.region_name
    , COUNT(DISTINCT CASE WHEN own_bike.owner = 'LAVKA' THEN dmlo.order_id END) AS order_cnt
  FROM {dm_lavka_order} AS dmlo
  LEFT JOIN {courier_tariff_own_bike_shifts} AS own_bike
    ON dmlo.courier_id = own_bike.courier_id::VARCHAR
    AND dmlo.local_order_taken_fact_dttm
      BETWEEN own_bike.local_bike_usage_start_dttm AND own_bike.local_bike_usage_end_dttm
  JOIN {stg_store} AS stg
    ON dmlo.place_id::VARCHAR = stg.store_id
  WHERE dmlo.local_arrival_to_customer_fact_dttm IS NOT NULL
    AND dmlo.local_created_dttm >= '2021-10-01'
    AND stg.country_name IN ('Россия')
  GROUP BY dmlo.local_created_dttm::DATE
    , date_trunc('month', dmlo.local_created_dttm)
    , dmlo.place_id
    , dmlo.country_name
    , dmlo.region_name
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE bike_orders;

-- Обогащаем предыдущую таблицу так, чтобы данных хватило для расчета статей
CREATE TEMPORARY TABLE bike_orders_enriched
ON COMMIT DROP
AS (
  SELECT b.lcl_calculation_dt
    , b.country_name
    , b.region_name
    , b.store_id
    , b.month_dt
    , EXTRACT(
        DAYS FROM b.month_dt + '1 month - 1 day'::INTERVAL
      )                                                              AS days_in_month
    , EXTRACT(
        DAYS FROM
          CASE WHEN b.month_dt = date_trunc('month', CURRENT_DATE - 1)::DATE
            THEN CURRENT_DATE - 1
            ELSE (b.month_dt + '1 month - 1 day'::INTERVAL)::DATE
          END
      )                                                              AS days_in_month_passed
    , b.order_cnt
    , SUM(b.order_cnt) OVER w                                        AS order_full_month_cnt
    , r.transport_reserve_value_lcy
  FROM bike_orders AS b
  LEFT JOIN {stg_reserve} AS r
    ON b.month_dt = r.month_dt
    AND b.country_name = r.country_name
  WINDOW w AS (PARTITION BY b.month_dt, b.country_name)
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE bike_orders_enriched;

------------------------------
-- Transport
------------------------------
CREATE TEMPORARY TABLE pre_stg_transport
ON COMMIT DROP
AS (
  SELECT e.lcl_calculation_dt
    , e.country_name
    , e.region_name
    , e.store_id

    -- План (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , mc.transport_plan_value_lcy
        * e.days_in_month_passed
        / e.days_in_month
        * e.order_cnt
        / e.order_full_month_cnt
        / cr.lcl_to_rub::NUMERIC                AS transport_value_lcy

    -- Финансовый итог (хранится в SP рублях, поэтому нужно переводить в локальную валюту)
    , CASE
        WHEN mc.fiscal_year_closed_period_flg
          THEN mc.transport_fact_value_lcy
                 * e.order_cnt
                 / e.order_full_month_cnt
                 / cr.lcl_to_rub
        ELSE 0.0
      END::NUMERIC                              AS transport_from_finance_department_value_lcy

    -- Резерв (хранится сразу в локальной валюте, поэтому переводить не нужно)
    , CASE
        WHEN e.transport_reserve_value_lcy IS NOT NULL
        AND e.transport_reserve_value_lcy != 0
          THEN e.transport_reserve_value_lcy
                 * e.order_cnt
                 / e.order_full_month_cnt
        ELSE 0.0
      END::NUMERIC                              AS transport_reserve_value_lcy

    , mc.fiscal_year_closed_period_flg
  FROM bike_orders_enriched AS e
  LEFT JOIN {stg_manual_correction} AS mc
    ON e.month_dt = mc.month_dt
    AND e.country_name = mc.country_name
  LEFT JOIN {stg_currency_rate} AS cr
    ON e.lcl_calculation_dt = cr.lcl_currency_rate_dt
    AND e.country_name = cr.country_name
  WHERE e.country_name IN ('Россия')
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE pre_stg_transport;

-- Формируем умное поле + добавляем неаллоцированные деньги
CREATE TABLE {stg_transport}
AS (
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id

    , transport_value_lcy
    , transport_from_finance_department_value_lcy
    , transport_reserve_value_lcy

    -- Умное поле: если месяц закрыт, то тут будет финансовый итог, а если нет, то связка "план + резерв"
    , CASE
        WHEN fiscal_year_closed_period_flg
          THEN transport_from_finance_department_value_lcy
        ELSE transport_value_lcy + transport_reserve_value_lcy
      END::NUMERIC                    AS transport_final_w_reserve_value_lcy

  FROM pre_stg_transport
  UNION ALL
  SELECT lcl_calculation_dt
    , country_name
    , region_name
    , store_id
    , '0'::NUMERIC                    AS transport_value_lcy
    , transport_unallocated_value_rub AS transport_from_finance_department_value_lcy
    , '0'::NUMERIC                    AS transport_reserve_value_lcy
    , transport_unallocated_value_rub AS transport_final_w_reserve_value_lcy
  FROM {stg_unallocated_by_days}
) DISTRIBUTED BY (lcl_calculation_dt, region_name, store_id);
ANALYZE {stg_transport};
GRANT ALL ON {stg_transport} TO "ed-avetisyan";
GRANT ALL ON {stg_transport} TO agabitashvili;
GRANT ALL ON {stg_transport} TO "robot-lavka-analyst";
