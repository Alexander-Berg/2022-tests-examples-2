INSERT INTO maas.subscriptions (
  maas_sub_id,   status,   maas_user_id,   phone_id,   coupon_id,   coupon_series_id,   
  tariff_info,   
  created_at,   updated_at,   expired_at
  )
VALUES (
  'sub_reserved', 'reserved', 'user_id1', 'phone_id1', 'coupon', 'coupon_series_id1', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
),
(
  'sub_reserved_to_cancel', 'reserved', 'user_id2', 'phone_id2', 'coupon', 'coupon_series_id1', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now() - interval '2 DAY' , now() - interval '2 DAY' , now() + interval '1 MONTH'
),
(
  'sub_canceled', 'canceled', 'user_id3', 'phone_id3', 'coupon', 'coupon_series_id1', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
),
(
  'sub_active', 'active', 'user_id4', 'phone_id4',  'coupon', 'coupon_series_id1', 
  ('maas_tariff_id', 10, 30, '100.50', '200.50'), 
  now(), now(), now() + interval '1 MONTH'
)
;


