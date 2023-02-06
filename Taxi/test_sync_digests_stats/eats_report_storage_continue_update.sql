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
     2, '2021-05-01',
     'place', 'address', 'mp', 'KZT',
     0, 0, 0, 0,
     0.0, 0.0, 0.0, 0.0,
     0.0, 0.0, 0, 0,
     3.0, 0.0,
     0, 0, 0, 0,
     '2021-04-01 00:00:00'::timestamptz
  );

INSERT INTO eats_report_storage.greenplum_sync(sync_name, last_sync_time)
VALUES ('sync-digests-stats', '2021-05-01 00:03:00'::timestamp)
