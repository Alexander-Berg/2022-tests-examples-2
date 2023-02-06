INSERT INTO maas.subscriptions (
  maas_sub_id,   status,   maas_user_id,   phone_id,   coupon_id,   coupon_series_id,   
  tariff_info,   
  created_at,   updated_at,   expired_at
  )
VALUES (
  'reserved_id', 'reserved', 'maas_user_id_1', 'reserved_phone_id', 'maas30000001', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
),
(
  'active_id', 'active', 'maas_user_id_2', 'active_phone_id', 'maas30000002', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
),
(
  'active_id_no_coupon', 'active', 'maas_user_id_3', 'active_phone_id_no_coupon', NULL, 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
)
;
