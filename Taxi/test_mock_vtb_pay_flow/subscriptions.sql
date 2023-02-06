INSERT INTO maas.subscriptions (
  maas_sub_id,   status,   maas_user_id,   phone_id,   coupon_id,   coupon_series_id,   
  tariff_info,   
  created_at,   updated_at,   expired_at
  )
VALUES (
  'sub_id', 'reserved', 'maas_user_id', 'phone_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now(), now(), now() + interval '100 YEAR'
);
