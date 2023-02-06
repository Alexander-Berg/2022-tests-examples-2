INSERT INTO eats_report_storage.agg_place_metric(
    place_id, utc_period_start_dttm, scale_name, brand_id, delivery_type,
    order_cancel_cnt, order_success_cnt, order_cnt, order_cancel_pcnt,
    revenue_earned_lcy, revenue_lost_lcy, revenue_lcy, revenue_average_lcy,
    currency_code, place_availability_pcnt, order_per_place_avg,
    plan_work_time_min, fact_work_time_min,
    _etl_processed_at 
) VALUES (
    2, '2021-11-11T00:00+03:00'::timestamptz, 'day', 1, 'marketplace',
    500, 725, 3000, 2.51,
    130.6, 60.44, 144000.7, 300.5,
    'RUB', 80.5, 122.6,
    2000000, 1000000,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  (
    2, '2021-11-10T00:00+03:00'::timestamptz, 'day', 1, 'marketplace',
    500, 625, 3000, 2.99,
    230.6, 60.44, 144000.7, 300.5,
    'RUB', 50.0, 122.6,
    2000000, 1000000,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  (
    2, '2021-11-09T00:00+03:00'::timestamptz, 'day', 1, 'marketplace',
    500, 525, 3000, 2.51,
    330.6, 60.44, 144000.7, 300.5,
    'RUB', 80.5, 122.6,
    2000000, 1000000,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  (
    2, '2021-11-08T00:00+03:00'::timestamptz, 'day', 1, 'marketplace',
    500, 425, 3000, 2.99,
    430.6, 60.44, 144000.7, 300.5,
    'RUB', 50.0, 122.6,
    2000000, 1000000,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  (
    2, '2021-11-07T00:00+03:00'::timestamptz, 'day', 1, 'marketplace',
    500, 325, 3000, 2.51,
    530.6, 60.44, 144000.7, 300.5,
    'RUB', 80.5, 122.6,
    2000000, 1000000,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  (
    2, '2021-11-06T00:00+03:00'::timestamptz, 'day', 1, 'marketplace',
    500, 225, 3000, 2.99,
    630.6, 60.44, 144000.7, 300.5,
    'RUB', 50.0,122.6,
    2000000, 1000000,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  (
    2, '2021-11-05T00:00+03:00'::timestamptz, 'day', 1, 'marketplace',
    5, 125, 30, 2.99,
    730.6, 60.44, 144000.7, 350.5,
    'RUB', 80.5, 122.6,
    2000000, 1000000,
    '2022-02-22T03:00+03:00'::timestamp
  );

INSERT INTO eats_report_storage.agg_place_metric(
    place_id, utc_period_start_dttm, scale_name, brand_id, delivery_type,
    order_cancel_cnt, order_success_cnt, order_cnt, order_cancel_pcnt,
    revenue_earned_lcy, revenue_lost_lcy, revenue_lcy, revenue_average_lcy,
    currency_code, place_availability_pcnt, order_per_place_avg,
    plan_work_time_min, fact_work_time_min,
    _etl_processed_at 
) VALUES (
    1, '2021-11-11T00:00+03:00'::timestamptz, 'day', 1, 'marketplace',
    0, 0, 1000, 0,
    0, 0, 0, 0,
    'RUB', 0, 0,
    0, 60,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  (
    1, '2021-11-10T00:00+03:00'::timestamptz, 'day', 1, 'marketplace',
    0, 0, 1000, 0,
    0, 0, 0, 0,
    'RUB', 0, 0,
    0, 59,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  (
    1, '2021-11-09T00:00+03:00'::timestamptz, 'day', 1, 'marketplace',
    0, 0, 0, 0,
    0, 0, 0, 0,
    'RUB', 0, 0,
    0, 1000000,
    '2022-02-22T03:00+03:00'::timestamp
  );

INSERT INTO eats_report_storage.agg_place_metric(
    place_id, utc_period_start_dttm, scale_name, brand_id, delivery_type,
    order_cancel_cnt, order_success_cnt, order_cnt, order_cancel_pcnt,
    revenue_earned_lcy, revenue_lost_lcy, revenue_lcy, revenue_average_lcy,
    currency_code, place_availability_pcnt, order_per_place_avg,
    plan_work_time_min, fact_work_time_min,
    _etl_processed_at 
) VALUES (
    2, '2021-11-11T03:00+03:00'::timestamptz, 'hour', 1, 'marketplace',
    0, 1000, 0, 0,
    0, 0, 0, 0,
    'RUB', 0, 0,
    0, 0,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  (
    2, '2021-11-10T03:00+03:00'::timestamptz, 'hour', 1, 'marketplace',
    0, 500, 0, 0,
    0, 0, 0, 0,
    'RUB', 0, 0,
    0, 0,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  (
    2, '2021-11-11T15:00+03:00'::timestamptz, 'hour', 1, 'marketplace',
    0, 500, 0, 0,
    0, 0, 0, 0,
    'RUB', 0, 0,
    0, 0,
    '2022-02-22T03:00+03:00'::timestamp
  );
