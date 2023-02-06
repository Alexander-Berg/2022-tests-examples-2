INSERT INTO eats_report_storage.agg_place_digests(
    place_id, period_date, place_name, place_address, delivery_type, currency_code,
    orders_total_cnt, orders_total_cnt_delta, orders_success_cnt, orders_success_cnt_delta,
    revenue_earned_lcy, revenue_earned_delta_lcy, revenue_lost_lcy, revenue_lost_delta_lcy,
    fines_lcy, fines_delta_lcy, delay_min, delay_delta_min,
    rating, rating_delta, fact_work_time_min, fact_work_time_delta_min, plan_work_time_min, plan_work_time_delta_min,
    _etl_processed_at)
VALUES
  ( 1, '2022-04-20', 'Place1', 'Москва', 'native', 'RUB',
    100, 10, 80, -10,
    15000.0, -230.0, 128.0, 128.0,
    50.0, 50.0, 100, -10,
    4.5, 0.1, 480, -120, 600, 0,
    '2021-09-09T03:00+03:00'::timestamp
  ),
  ( 2, '2022-04-20', 'Place2', 'Москва', 'native', 'RUB',
    0, -10, 0, -10,
    15000.0, -230.0, 128.0, 128.0,
    50.0, 50.0, 100, -10,
    4.5, 0.1, 480, -120, 600, 0,
    '2021-09-09T03:00+03:00'::timestamp
  ),
  ( 3, '2022-04-20', 'Place3', 'Москва', 'native', 'RUB',
    100, 10, 80, -10,
    15000.0, -230.0, 128.0, 128.0,
    50.0, 50.0, 100, -10,
    4.5, 0.1, 0, -120, 600, 0,
    '2021-09-09T03:00+03:00'::timestamp
  ),
  ( 4, '2022-04-20', 'Place4', 'Москва', 'native', 'RUB',
    100, 10, 80, -10,
    15000.0, -230.0, 128.0, 128.0,
    50.0, 50.0, 100, -10,
    4.5, 0.1, NULL, -120, 600, 0,
    '2021-09-09T03:00+03:00'::timestamp
  );


INSERT INTO eats_report_storage.agg_place_metric(
    place_id, utc_period_start_dttm, scale_name, brand_id, delivery_type,
    order_cancel_cnt, order_success_cnt, order_cnt, order_cancel_pcnt,
    revenue_earned_lcy, revenue_lost_lcy, revenue_lcy, revenue_average_lcy,
    currency_code, place_availability_pcnt, order_per_place_avg,
    plan_work_time_min, fact_work_time_min,
    _etl_processed_at 
) VALUES
  ( 1, '2022-04-20T00:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    50, 150, 200, 25,
    1500.0, 500.0, 2000.0, 10.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 1, '2022-04-20T00:00+03:00'::timestamptz, 'hour', 1, 'marketplace',
    5, 15, 20, 25,
    150.0, 50.0, 200.0, 10.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 1, '2022-04-20T23:59:59+03:00'::timestamptz, 'hour', 1, 'marketplace',
    5, 15, 20, 25,
    150.0, 50.0, 200.0, 10.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 1, '2022-04-20T23:00+02:00'::timestamptz, 'hour', 1, 'marketplace',
    50, 150, 200, 25,
    1500.0, 500.0, 2000.0, 10.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 1, '2022-04-13T00:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    0, 100, 100, 0,
    1500.0, 0.0, 1500.0, 15.0,
    'RUB', NULL, 10,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 1, '2022-04-13T00:00+03:00'::timestamptz, 'hour', 1, 'marketplace',
    0, 10, 10, 0,
    150.0, 0.0, 150.0, 15.0,
    'RUB', NULL, 10,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 1, '2022-04-13T23:59:59+03:00'::timestamptz, 'hour', 1, 'marketplace',
    0, 10, 10, 0,
    150.0, 0.0, 150.0, 15.0,
    'RUB', NULL, 10,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 1, '2022-04-13T23:00+02:00'::timestamptz, 'hour', 1, 'marketplace',
    0, 100, 100, 0,
    1500.0, 0.0, 1500.0, 15.0,
    'RUB', NULL, 10,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  );


INSERT INTO eats_report_storage.agg_place_digests_fallback(
    place_id, period_date,
    orders_total_cnt, orders_total_cnt_delta, orders_success_cnt, orders_success_cnt_delta,
    revenue_earned_lcy, revenue_earned_delta_lcy, revenue_lost_lcy, revenue_lost_delta_lcy,
    _etl_processed_at)
VALUES
  ( 1, '2022-04-20',
    200, 50, 100, -50,
    2999.99, 0.0, 1000.01, 1000.01,
    '2021-09-09T03:00+03:00'::timestamp
  ),
  ( 1, '2022-04-19',
    0, -10, 0, -10,
    15000.0, -230.0, 128.0, 128.0,
    '2021-09-09T03:00+03:00'::timestamp
  ),
  ( 2, '2022-04-20',
    100, 10, 80, -10,
    15000.0, -230.0, 128.0, 128.0,
    '2021-09-09T03:00+03:00'::timestamp
  );
