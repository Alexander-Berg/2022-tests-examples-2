INSERT INTO maas.subscriptions (
  maas_sub_id,   status,   maas_user_id,   phone_id,   coupon_id,   coupon_series_id,   
  tariff_info,   
  created_at,   updated_at,   expired_at
  )
VALUES (
  'reserved_id', 'reserved', 'maas_user_id', 'phone_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
),
(
  'active_id', 'active', 'maas_user_id', 'phone_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
),
(
  'canceled_id', 'canceled', 'maas_user_id', 'phone_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
),
(
  'expired_id', 'expired', 'maas_user_id', 'phone_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now() - interval '2 MONTH', now() - interval '2 MONTH', now() - interval '1 MONTH'
),
(
  'active_expired_id', 'active', 'maas_user_id', 'phone_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now() - interval '2 MONTH', now() - interval '2 MONTH', now() - interval '1 MONTH'
);
