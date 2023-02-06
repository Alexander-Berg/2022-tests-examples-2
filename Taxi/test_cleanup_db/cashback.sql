INSERT INTO cashback.order_rates (order_id, rates, updated)
VALUES
('order_id_1', '{}'::jsonb, '2020-11-01T12:00:00+0'),
('order_id_2', '{}'::jsonb, '2020-11-01T12:00:00+0');

INSERT INTO cashback.order_clears (order_id, currency, value, cashback_sum,
                                   version, updated)
VALUES
('order_id_1', 'RUB', '10', '2', 1, '2020-11-01T12:00:00+0'),
('order_id_2', 'RUB', '10', '2', 1, '2021-11-01T12:00:00+0');


INSERT INTO cashback.events
  (id, external_ref, type, status, value, currency, created, updated, yandex_uid)
VALUES
  ('event_id_33', 'order_id_1', 'withdraw', 'done', '30', 'EUR', '2019-11-01T12:00:00+0', '2020-11-01T12:00:00+0', 'yandex_uid'),
  ('event_id_4', 'order_id_2', 'withdraw', 'new', '11', 'RUB', '2019-11-01T12:00:00+0', '2020-11-01T12:00:00+0', 'yandex_uid'),
  ('event_id_5', 'order_id_3', 'charge', 'done', '11', 'RUB', '2019-11-01T12:00:00+0', '2020-11-01T12:00:00+0', 'yandex_uid');
