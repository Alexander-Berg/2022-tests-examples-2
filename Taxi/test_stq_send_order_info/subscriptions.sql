INSERT INTO maas.subscriptions (
  maas_sub_id,   status,   maas_user_id,   phone_id,   coupon_id,   coupon_series_id,   
  tariff_info,   
  created_at,   updated_at,   expired_at
  )
VALUES (
  'sub_id_1', 'active', 'user_id1', '612ca45973872fb3b5b9b40e', 'coupon_id_1', 'coupon_series_id1',
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
)
;
