INSERT INTO maas.subscriptions (
  maas_sub_id,   status,   maas_user_id,   phone_id,   coupon_id,   coupon_series_id,   
  tariff_info,   
  created_at,   updated_at,   expired_at
  )
VALUES (
  'reserved_id', 'reserved', 'maas_user_id', 'reserved_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 day'
),
(
  'promoted_reserved_id', 'reserved', 'maas_user_id', 'promoted_reserved_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 day'
),
(
  'active_id', 'active', 'maas_user_id', 'active_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 day'
),
(
  'canceled_id', 'canceled', 'maas_user_id', 'canceled_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 day'
),
(
  'promoted_canceled_id', 'canceled', 'maas_user_id', 'promoted_canceled_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now(), now(), now() + interval '1 day'
),
(
  'expired_id', 'expired', 'maas_user_id', 'expired_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now() - interval '2 day', now() - interval '2 day', now() - interval '1 day'
),
(
  'expired_no_promo_id', 'expired', 'maas_user_id', 'expired_no_promo_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now() - interval '2 day', now() - interval '2 day', now() - interval '1 day'
),
(
  'active_expired_id', 'active', 'maas_user_id', 'active_expired_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now() - interval '2 day', now() - interval '2 day', now() - interval '1 day'
),
(
  'active_expired_no_promo_id', 'active', 'maas_user_id', 'active_expired_no_promo_id', 'coupon_id', 'coupon_series_id', 
  ('maas_tariff_id', 10, 31, '100.50', '200.50'), 
  now() - interval '2 day', now() - interval '2 day', now() - interval '1 day'
)

;


