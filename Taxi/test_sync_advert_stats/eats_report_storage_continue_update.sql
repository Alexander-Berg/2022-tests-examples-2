INSERT INTO eats_report_storage.place_advert_metric(
    brand_id,
    place_id,
    banner_id,
    utc_period_start_dttm,
    scale_name,
    place_advert_status,
    shows,
    clicks,
    ad_orders,
    ad_gmv,
    organic_returner_from_ad_gmv,
    spent_value,
    profit_value,
    ad_newcommer,
    ad_newcommer_gmv,
    returner_from_ad_orders,
    returner_from_ad_gmv,
    organic_newcommer,
    organic_newcommer_gmv,
    returner_from_organic_orders,
    returner_from_organic_gmv,
    conversion_orders_in_clicks,
    averagecpc,
    _etl_processed_at)
VALUES
  (
    1,
    1,
    1,
    '2021-09-10 00:00+00:00'::timestamptz,
    'month',
    'active',
    1,
    1,
    1,
    1.1,
    1.1,
    1.1,
    1.1,
    1,
    1.1,
    1,
    1.1,
    1,
    1.1,
    1,
    1.1,
    1,
    1.1,
    '2021-09-10 03:00+00:00'::timestamptz
  ),
  (
    2,
    2,
    2,
    '2021-09-10 00:00+00:00'::timestamptz,
    'month',
    'active',
    2,
    2,
    2,
    2.2,
    2.2,
    2.2,
    2.2,
    2,
    2.2,
    2,
    2.2,
    2,
    2.2,
    2,
    2.2,
    2,
    2.2,
    '2021-09-10 02:00+00:00'::timestamptz
  ),
  (
    3,
    3,
    3,
    '2021-09-10 00:00+00:00'::timestamptz,
    'month',
    'active',
    3,
    3,
    3,
    3.3,
    3.3,
    3.3,
    3.3,
    3,
    3.3,
    3,
    3.3,
    3,
    3.3,
    3,
    3.3,
    3,
    3.3,
    '2021-09-10 01:00+00:00'::timestamptz
  );
