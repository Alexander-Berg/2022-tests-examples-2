SET TIME ZONE 'Europe/Moscow';

INSERT INTO eda_cdm_supply.agg_place_promo_metric(
    place_id,
    msk_period_start_dttm,
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
    _etl_processed_dttm)
VALUES
  (
     1,
     '2021-07-01 03:00'::timestamp,
     'monthly',
     1,
     'native',
     -1,
     2,
     1,
     2,
     5,
     5,
     5,
     3,
     4,
     1,
     2,
     3,
     5,
     '2021-06-30 03:03:30'::timestamp + interval '1 minute'
  ),
  (
     1,
     '2021-06-30 03:03:30'::timestamp,
     'weekly',
     1,
     'native',
     -1,
     2,
     1,
     2,
     5,
     5,
     5,
     3,
     4,
     1,
     2,
     3,
     5,
     '2021-06-30 00:03:30'::timestamp + interval '1 minute'
  ),
  (
     1,
     '2021-06-30 00:00+03:00'::timestamp,
     'weekly',
     1,
     'native',
     -1,
     2,
     1,
     2,
     5,
     5,
     5,
     3,
     4,
     1,
     2,
     3,
     5,
     '2021-06-30 00:03:30'::timestamp + interval '2 minute'
  ),
  (
     1,
     '2021-06-30 00:00+03:00'::timestamp,
     'hourly',
     1,
     'native',
     -1,
     2,
     1,
     2,
     5,
     5,
     5,
     3,
     4,
     1,
     2,
     3,
     5,
     '2021-06-30 00:03:30'::timestamp + interval '2 minute'
  ),
  (
     10,
     '2021-06-30 00:00+03:00'::timestamp,
     'hourly',
     1,
     'native',
     -1,
     2,
     1,
     2,
     5,
     5,
     5,
     3,
     4,
     1,
     2,
     3,
     5,
     '2021-06-30 00:03:30'::timestamp + interval '2 minute'
  ),
  (
     10,
     '2021-06-30 00:00'::timestamp,
     'weekly',
     1,
     'native',
     -1,
     2,
     1,
     2,
     5,
     5,
     5,
     3,
     4,
     1,
     2,
     3,
     5,
     '2021-06-30 00:03:30'::timestamp + interval '2 minute'
  );
