INSERT INTO maas.users (maas_user_id, phone_id, personal_phone_id) 
VALUES
('user_1', 'user_1_phone_id', 'user_1_phone_pd_id'),
('user_2', 'user_2', 'user_2_phone_pd_id');

INSERT INTO maas.subscriptions
(
	maas_sub_id,
	status,
	maas_user_id,
	phone_id,
	coupon_id,
	coupon_series_id,
	tariff_info,
	created_at,
	updated_at,
	expired_at
)
VALUES
(
	'user_1_sub_id_1',
	'active',
	'user_1',
	'user_1_phone_id',
	'user_1_coupon_id_1',
	'',
	('', 0, 0, 0, 0)::maas.tariff_info,
	'2021-12-12T15:00:00Z',
	'2021-12-12T15:10:00Z',
	'2021-12-31T15:00:00Z'
),
(
	'user_1_sub_id_2',
	'expired',
	'user_1',
	'user_1_phone_id',
	'user_1_coupon_id_2',
	'',
	('', 0, 0, 0, 0)::maas.tariff_info,
	'2021-10-12T15:00:00Z',
	'2021-10-12T15:10:00Z',
	'2021-10-31T15:00:00Z'
),
(
	'user_2_sub_id_1',
	'active',
	'user_2',
	'user_2_phone_id',
	'user_2_coupon_id_1',
	'',
	('', 0, 0, 0, 0)::maas.tariff_info,
	'2021-12-12T14:00:00Z',
	'2021-12-12T14:10:00Z',
	'2021-12-31T14:00:00Z'
),
(
	'user_2_sub_id_2',
	'expired',
	'user_2',
	'user_2_phone_id',
	'user_2_coupon_id_2',
	'',
	('', 0, 0, 0, 0)::maas.tariff_info,
	'2021-10-12T14:00:00Z',
	'2021-10-12T14:10:00Z',
	'2021-10-31T14:00:00Z'
);

INSERT INTO maas.orders (order_id, maas_user_id, phone_id, maas_sub_id, is_maas_order)
VALUES
  ('order_id_1', 'user_1', 'user_1_phone_id', 'user_1_sub_id_1', TRUE),
  ('order_id_2', 'user_2', 'user_2_phone_id', 'user_1_sub_id_2', TRUE),
  ('order_id_3', 'user_1', 'user_1_phone_id', 'user_1_sub_id_1', TRUE);
