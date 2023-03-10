SET TIME ZONE 'UTC';

INSERT INTO eats_report_storage.promo_agg_stats(
    place_id,
    utc_period_start_dttm,
    scale_name,
    brand_id,
    delivery_type,
    promo_id,
    promo_type_id,
    place_revenue_lcy,
    place_lost_revenue_lcy,
    successful_order_cnt,
    order_cancelled_by_place_cnt,
    new_user_cnt,
    discount_for_item_list_cnt,
    one_plus_one_cnt,
    conversion_to_order_pcnt,
    unique_user_visit_cnt,
    user_w_order_cnt,
    average_order_cost_lcy,
    _etl_processed_at)
VALUES
  (
     1,
     '2021-06-30 00:03:31'::timestamp,
     'week',
     1,
     'native',
     -1,
     2,
     1,
     2,
     5,
     5,
     9,
     3,
     4,
     1,
     2,
     3,
     5,
     '2021-06-30 00:03:31'::timestamp
  ),
  (
     1,
     '2021-06-30 00:03:30'::timestamp - interval '1 minute',
     'week',
     1,
     'native',
     -1,
     2,
     1,
     2,
     5,
     5,
     8,
     3,
     4,
     1,
     2,
     3,
     5,
     '2021-06-30 00:03:30'::timestamp - interval '2 hour'
  ),
  (
     1,
     '2021-06-30 00:03:30'::timestamp - interval '3 hour',
     'week',
     1,
     'native',
     -1,
     2,
     1,
     2,
     5,
     5,
     6,
     3,
     4,
     1,
     2,
     3,
     5,
     '2021-06-30 00:03:30'::timestamp - interval '6 hour'
  )
  ,
  (1,
   '2021-07-01 03:00+03:00'::timestamptz,
   'month',
   1,
   'native',
   -1,
   2,
   1,
   2,
   5,
   5,
   7,
   3,
   4,
   1,
   2,
   3,
   5,
   '2021-06-30 00:03:30'::timestamp)
  ;

INSERT INTO eats_report_storage.greenplum_sync(sync_name, last_sync_time)
VALUES ('sync-promo-stats', '2021-05-30 00:03:30'::timestamp)
