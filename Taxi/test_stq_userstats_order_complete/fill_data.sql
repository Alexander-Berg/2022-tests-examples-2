INSERT INTO userstats.processed_orders (identity_type, order_id)
VALUES
  ('phone_id', 'order1'),
  ('yandex_uid', 'order1');

INSERT INTO userstats.orders_counters
(
  id,
  identity_type,
  identity_value,
  counter_value,
  counted_from,
  counted_to,
  tariff_class,
  brand,
  payment_type
)
VALUES
(
  '6bf050a6-f426-4d2b-b6c4-044a3d4d1480',
  'phone_id',
  '000000000000000000000000',
  1,
  '2019-12-11 12:00:00+03',
  '2019-12-11 12:00:00+03',
  'econom',
  'yataxi',
  'card'
),
(
  '52d8c143-d556-42ff-8f04-31445b59f039',
  'yandex_uid',
  '0123456789',
  1,
  '2019-12-11 12:00:00+03',
  '2019-12-11 12:00:00+03',
  'econom',
  'yataxi',
  'card'
);

INSERT INTO userstats.recent_orders (order_counter_id, order_created_at)
VALUES
  ('52d8c143-d556-42ff-8f04-31445b59f039', '2019-12-11 12:00:00+03');
