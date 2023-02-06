INSERT INTO maas.subscriptions (
  maas_sub_id,   status,   maas_user_id,   phone_id,   coupon_id,   coupon_series_id,   
  tariff_info,   
  created_at,   updated_at,   expired_at
  )
VALUES (
  'sub_id1', 'reserved', 'user_id1', 'phone_id1', 'reserved_coupon', 'coupon_series_id1', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
),
(
  'sub_id2', 'reserved', 'user_id2', 'phone_id2', 'canceled_coupon', 'coupon_series_id1', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now() - interval '2 DAY' , now() - interval '2 DAY' , now() + interval '1 MONTH'
),
(
  'sub_id3', 'canceled', 'user_id3', 'phone_id3', 'canceled_coupon', 'coupon_series_id1', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now() - interval '2 DAY' , now() - interval '2 DAY' , now() + interval '1 MONTH'
),
(
  'sub_id4', 'active', 'user_id4', 'phone_id4',  'active_coupon', 'coupon_series_id1', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now() - interval '1 MONTH' , now() - interval '1 MONTH' , now() + interval '5 MINUTE'
),
(
  'sub_id5', 'active', 'user_id5', 'phone_id5', 'expired_coupon', 'coupon_series_id1', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now() - interval '1 MONTH' , now() - interval '1 MONTH' , now() - interval '5 MINUTE'
),
(
  'sub_id6', 'expired', 'user_id6', 'phone_id6', 'expired_coupon', 'coupon_series_id1', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now() - interval '1 MONTH' , now() - interval '1 MONTH' , now() - interval '5 MINUTE'
)
;


