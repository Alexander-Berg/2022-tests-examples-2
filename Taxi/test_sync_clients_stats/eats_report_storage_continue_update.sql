SET TIME ZONE 'UTC';

INSERT INTO eats_report_storage.place_clients_metric(
    place_id,
    brand_id,
    utc_period_start_dttm,
    scale_name,
    users_with_1_order_cnt,
    users_with_2_orders_cnt,
    users_with_3_orders_and_more_cnt,
    unique_users_cnt,
    newcommers_cnt,
    oldcommers_cnt,
    oldcommers_gmv_pcnt,
    oldcommers_gmv_lcy,
    newcommers_gmv_lcy,
    _etl_processed_at)
VALUES
  (
     1,
     2,
     '2021-06-30 00:03:29'::timestamp,
     'week',
     1,
     2,
     3,
     4,
     5,
     6,
     1.7,
     1.8,
     1.9,
     '2021-06-30 00:03:29'::timestamp
  ),
  (
     1,
     2,
     '2021-06-30 00:03:30'::timestamp - interval '1 minute',
     'week',
     11,
     12,
     13,
     14,
     15,
     16,
     1.7,
     1.8,
     1.9,
     '2021-06-30 00:03:30'::timestamp - interval '2 hour'
  ),
  (
     1,
     2,
     '2021-06-30 00:03:30'::timestamp - interval '3 hour',
     'week',
     21,
     22,
     23,
     24,
     25,
     26,
     2.7,
     2.8,
     2.9,
     '2021-06-30 00:03:30'::timestamp - interval '6 hour'
  ),
  (
     1,
     2,
     '2021-07-01 03:00+03:00'::timestamptz,
     'month',
     31,
     32,
     33,
     34,
     35,
     36,
     3.7,
     3.8,
     3.9,
     '2021-06-30 00:03:30'::timestamp
  );

INSERT INTO eats_report_storage.greenplum_sync(sync_name, last_sync_time)
VALUES ('sync-clients-stats', '2021-05-30 00:03:30'::timestamp)
