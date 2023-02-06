INSERT INTO userstats.orders_counters
(
  counter_value,
  counted_from,
  counted_to,
  tariff_class,
  brand,
  payment_type,
  identity_type,
  identity_value
)
VALUES
(1, '2019-12-11 12:00:00+03', '2019-12-11 12:00:00+03', 'econom',  'yataxi', 'card', 'phone_id', '000000000000000000000001'),
(1, '2019-12-11 12:00:00+03', '2019-12-11 12:00:00+03', 'econom',  'yataxi', 'card', 'yandex_uid', '0000000001'),
(1, '2019-12-11 12:00:00+03', '2019-12-11 12:00:00+03', 'econom',  'yataxi', 'card', 'card_persistent_id', '00000000000000000000000000000001'),
(1, '2019-12-11 12:00:00+03', '2019-12-11 12:00:00+03', 'econom',  'yataxi', 'card', 'device_id', '00000000-0000-0000-0000-000000000001'),

(1, '2019-12-11 12:00:00+03', '2019-12-11 12:00:00+03', 'econom',  'yataxi', 'card', 'phone_id', '000000000000000000000002'),
(1, '2019-12-11 12:00:00+03', '2019-12-11 12:00:00+03', 'econom',  'yataxi', 'card', 'card_persistent_id', '00000000000000000000000000000002'),

(2, '2019-12-13 12:00:00+03', '2019-12-14 12:00:00+03', 'comfort', 'yataxi', 'card', 'phone_id', '000000000000000000000002'),
(2, '2019-12-13 12:00:00+03', '2019-12-14 12:00:00+03', 'comfort', 'yataxi', 'card', 'card_persistent_id', '00000000000000000000000000000002'),

(3, '2019-12-15 12:00:00+03', '2019-12-16 12:00:00+03', 'comfort', 'yataxi', 'cash', 'phone_id', '000000000000000000000002'),
(3, '2019-12-17 12:00:00+03', '2019-12-18 12:00:00+03', NULL,      'yataxi', 'cash', 'phone_id', '000000000000000000000002')
;