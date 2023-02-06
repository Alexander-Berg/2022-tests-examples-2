SET TIME ZONE 'UTC';

INSERT INTO eats_report_storage.agg_place_digests (
    place_id, period_date,
    place_name, place_address, delivery_type, currency_code,
    orders_total_cnt, orders_total_cnt_delta, orders_success_cnt, orders_success_cnt_delta,
    revenue_earned_lcy, revenue_earned_delta_lcy, revenue_lost_lcy, revenue_lost_delta_lcy,
    fines_lcy, fines_delta_lcy, delay_min, delay_delta_min,
    rating, rating_delta,
    fact_work_time_min, fact_work_time_delta_min, plan_work_time_min, plan_work_time_delta_min,
    _etl_processed_at)
VALUES
  (
     1, '2021-05-01',
     'place1', 'address1', 'native', 'RUB',
     100, 10, 80, -10,
     111.1111, -11.1111, 1.1234, 1.1234,
     10.9999, 1.9999, 100, -10,
     4.5, 0.1,
     1000, -100, 1111, 111,
     '2021-05-01 00:00:00'::timestamptz
  ),
  (
     2, '2021-04-29',
     'place2', 'address2', 'marketplace', 'BYN',
     200, 20, 60, -20,
     222.2222, -22.2222, 2.1234, 2.1234,
     20.9999, 2.9999, 200, -20,
     3.5, 0.2,
     2000, -200, 2222, 222,
     '2021-05-01 00:00:00'::timestamptz
  );

INSERT INTO eats_report_storage.greenplum_sync(sync_name, last_sync_time)
VALUES ('sync-digests-stats', '2021-05-01 00:03:00'::timestamp)
