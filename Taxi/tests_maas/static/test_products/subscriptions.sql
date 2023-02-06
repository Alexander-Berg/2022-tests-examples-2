INSERT INTO maas.subscriptions (
  maas_sub_id,   status,   maas_user_id,   phone_id,   coupon_id,   coupon_series_id,   
  tariff_info,   
  created_at,   updated_at,   expired_at
  )
VALUES (
  'active_id', 'active', 'active_maas_user_id', 'active_phone_id', 'test_coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
),
(
  'expired_id', 'expired', 'expire_maas_user_id', 'expired_phone_id', 'test_coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now() - interval '2 MONTH', now() - interval '2 MONTH', now() - interval '1 MONTH'
)
;


