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
  ( 2, '2022-04-20', 'Place1', 'Москва', 'native', 'RUB',
    100, 10, 80, -10,
    15000.0, -230.0, 128.0, 128.0,
    50.0, 50.0, 100, -10,
    4.5, 0.1, 480, -120, 600, 0,
    '2021-09-09T03:00+03:00'::timestamp
  ),
  ( 3, '2022-04-20', 'Place1', 'Москва', 'native', 'RUB',
    100, 10, 80, -10,
    15000.0, -230.0, 128.0, 128.0,
    50.0, 50.0, 100, -10,
    4.5, 0.1, 480, -120, 600, 0,
    '2021-09-09T03:00+03:00'::timestamp
  ),
  ( 4, '2022-04-20', 'Place1', 'Москва', 'native', 'RUB',
    0, -100, 0, -80,
    0.0, -15000.0, 0.0, -128.0,
    0.0, -50.0, 0, -10,
    4.5, 0.0, 0, -120, 600, 0,
    '2021-09-09T03:00+03:00'::timestamp
  ),
  ( 5, '2022-04-20', 'Place1', 'Москва', 'native', 'RUB',
    0, -100, 0, -80,
    0.0, -15000.0, 0.0, -128.0,
    0.0, -50.0, 0, -10,
    4.5, 0.0, 300, 0, 600, 0,
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
  ( 1, '2022-04-13T12:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    0, 90, 90, 25,
    15230.0, 0, 15230.0, 1.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 1, '2022-04-20T12:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    20, 80, 100, 20,
    15000.0, 128.0, 15128.0, 1.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 2, '2022-04-13T12:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    20, 80, 100, 20,
    15230.0, 0, 15230.0, 1.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 2, '2022-04-20T12:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    20, 105, 125, 16,
    15000.0, 128.0, 15128.0, 1.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 3, '2022-04-13T12:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    0, 90, 90, 25,
    15300.0, 50.0, 15350.0, 1.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 3, '2022-04-20T12:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    20, 80, 100, 20,
    15100.0, 228.0, 15328.0, 1.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 4, '2022-04-13T12:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    0, 90, 90, 25,
    15230.0, 0, 15230.0, 1.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 4, '2022-04-20T12:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    20, 80, 100, 20,
    15000.0, 128.0, 15128.0, 1.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 5, '2022-04-13T12:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    0, 90, 90, 25,
    15230.0, 0, 15230.0, 1.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  ),
  ( 5, '2022-04-20T12:00+04:00'::timestamptz, 'hour', 1, 'marketplace',
    20, 80, 100, 20,
    15000.0, 128.0, 15128.0, 1.0,
    'RUB', NULL, 15,
    NULL, NULL,
    '2022-02-22T03:00+03:00'::timestamp
  );
