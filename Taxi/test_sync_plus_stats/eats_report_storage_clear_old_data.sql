SET TIME ZONE 'UTC';

INSERT INTO eats_report_storage.place_plus_metric(
    brand_id,
    place_id,
    utc_period_start_dttm,
    scale_name,
    place_plus_status,
    user_w_plus_gmv_lcy,
    user_wo_plus_gmv_lcy,
    user_w_plus_order_cnt,
    user_wo_plus_order_cnt,
    cashback_by_place_lcy,
    cashback_spent_by_user_lcy,
    avg_cashback_by_place_pcnt,
    new_user_w_plus_cnt,
    new_user_wo_plus_cnt,
    user_w_plus_ltv_lcy,
    user_wo_plus_ltv_lcy,
    user_w_plus_frequency_val,
    user_wo_plus_frequency_val,
    _etl_processed_at)
VALUES
  (
     1,
     1,
     '2021-06-30 00:03:30+00'::timestamp,
     'week',
     'partly_active',
     0.1,
     0.2,
     1,
     2,
     0.3,
     0.4,
     0.5,
     3,
     4,
     0.6,
     0.7,
     0.8,
     0.9,
     '2021-06-30 00:03:30+00'::timestamp
  ),
  (
     1,
     1,
     '2021-06-30 00:03:30+00'::timestamp - interval '4 hours',
     'week',
     'partly_active',
     1.1,
     1.2,
     1,
     2,
     1.3,
     1.4,
     1.5,
     3,
     4,
     1.6,
     1.7,
     1.8,
     1.9,
     '2021-06-30 00:03:30+00'::timestamp
  ),
  (
     1,
     1,
     '2021-06-30 00:03:30+00'::timestamp - interval '4 hours' - interval '1 minutes',
     'week',
     'partly_active',
     5.1,
     5.2,
     1,
     2,
     5.3,
     5.4,
     5.5,
     3,
     4,
     5.6,
     5.7,
     5.8,
     5.9,
     '2021-06-30 00:03:30+00'::timestamp
  ),
  (
     1,
     1,
     '2021-06-30 00:03:30+00'::timestamp - interval '6 hour',
     'week',
     'partly_active',
     2.1,
     2.2,
     1,
     2,
     2.3,
     2.4,
     2.5,
     3,
     4,
     2.6,
     2.7,
     2.8,
     2.9,
     '2021-06-30 00:03:30+00'::timestamp
  ),
  (
     1,
     1,
     '2021-06-30 00:03:30+00'::timestamp - interval '8 hour',
     'week',
     'partly_active',
     3.1,
     3.2,
     1,
     2,
     3.3,
     3.4,
     3.5,
     3,
     4,
     3.6,
     3.7,
     3.8,
     3.9,
     '2021-06-30 00:03:30+00'::timestamp
  );