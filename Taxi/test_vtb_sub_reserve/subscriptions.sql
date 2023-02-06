INSERT INTO maas.subscriptions (
  maas_sub_id,   status,   maas_user_id,   phone_id,   coupon_id,   coupon_series_id,   
  tariff_info,   
  created_at,   updated_at,   expired_at, status_history
  )
VALUES (
  'sub_id', 'reserved', 'maas_user_id', 'phone_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now(), now(), now() + interval '100 YEAR',
  array[(now(), 'reserved', 'vtb reserve request')]::maas.status_history[]
),
(
  'fail_reserved1', 'reserved', 'maas_user_id1', 'phone_id1', NULL, 'coupon_series_id', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  timestamptz('2021-06-30T21:01:00.00Z'), timestamptz('2021-07-02T00:01:00.00Z'), 
  timestamptz('2021-07-01T00:01:00.00Z') + interval '100 YEAR', -- rough expired_at
  array[(timestamptz('2021-06-30T21:01:00.00Z'), 'reserved', 'vtb_request')]::maas.status_history[]
),
(
  'fail_reserved2', 'reserved', 'maas_user_id2', 'phone_id2', NULL, 'coupon_series_id', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  timestamptz('2021-07-01T20:59:00.00Z'), timestamptz('2021-07-02T00:01:00.00Z'), 
  timestamptz('2021-07-01T00:01:00.00Z') + interval '100 YEAR', -- rough expired_at
  array[(timestamptz('2021-07-01T20:59:00.00Z'), 'reserved', 'vtb_request')]::maas.status_history[]
),
(
  'fail_reserved3', 'reserved', 'maas_user_id3', 'phone_id3', NULL, 'coupon_series_id', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  timestamptz('2021-07-01T21:01:00.00Z'), timestamptz('2021-07-02T00:01:00.00Z'), 
  timestamptz('2021-07-01T00:01:00.00Z') + interval '100 YEAR', -- rough expired_at
  array[(timestamptz('2021-07-02T00:01:00.00Z'), 'reserved', 'vtb_request')]::maas.status_history[]
),
(
  'fail_reserved4', 'reserved', 'maas_user_id4', 'phone_id4', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  timestamptz('2021-07-02T21:01:00.00Z'), timestamptz('2021-07-02T00:01:00.00Z'), 
  timestamptz('2021-08-02T01:00:00.00Z') + interval '100 YEAR',
  array[(timestamptz('2021-07-02T00:01:00.00Z'), 'reserved', 'vtb_request')]::maas.status_history[]
)
;


