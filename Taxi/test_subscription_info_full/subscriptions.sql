INSERT INTO maas.subscriptions (
  maas_sub_id,   status,   maas_user_id,   phone_id,   coupon_id,   coupon_series_id,   
  tariff_info,   
  created_at,   updated_at,   expired_at
  )
VALUES (
  'active_id', 'active', 'maas_user_id', 'active_phone_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
),
(
  'expired_id', 'expired', 'maas_user_id', 'expired_phone_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  '2021-05-10T00:00:00+03:00', '2021-05-10T00:00:00+03:00', '2021-06-10T00:00:00+03:00'
),
(
  'reserved_id', 'reserved', 'maas_user_id', 'reserved_phone_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
)
;
