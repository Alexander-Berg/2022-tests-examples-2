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
  '0008c143-d556-42ff-8f04-31445b59f039',
  'yandex_uid',
  '0123456789',
  50,
  '2015-01-01 12:00:00+03',
  '2019-12-11 12:00:00+03',
  'econom',
  'yataxi',
  'card'
);

INSERT INTO userstats.recent_orders (order_counter_id, order_created_at)
VALUES
  ('0008c143-d556-42ff-8f04-31445b59f039', '2019-11-09 12:00:00+03'),
  -- граница 2019-11-30 23:59:30 округлится в 2019-12-01T00:00:00
  ('0008c143-d556-42ff-8f04-31445b59f039', '2019-11-30 23:59:59+03'),
  ('0008c143-d556-42ff-8f04-31445b59f039', '2019-12-01 00:00:01+03'),
  ('0008c143-d556-42ff-8f04-31445b59f039', '2019-12-09 12:00:00+03');
