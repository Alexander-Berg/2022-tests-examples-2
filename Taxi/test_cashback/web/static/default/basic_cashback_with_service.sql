INSERT INTO cashback.events
  (id, external_ref, type, status, value, currency, created, service, yandex_uid)
VALUES
  ('event_id_1', 'order_id_1', 'charge', 'new', '50', 'RUB', '2019-08-15T12:00:00+0', 'uber', 'yandex_uid_1'),
  ('event_id_2', 'order_id_1', 'charge', 'done', '200', 'RUB', '2019-08-15T13:00:00+0', 'yataxi', 'yandex_uid_1'),
  ('event_id_3', 'order_id_1', 'withdraw', 'new', '30', 'RUB', '2019-08-15T14:00:00+0', 'eda', 'yandex_uid_1'),
  ('event_id_4', 'order_id_2', 'withdraw', 'new', '11', 'RUB', '2019-08-15T15:00:00+0', 'lavka', 'yandex_uid_1'),
  ('event_id_5', 'order_id_3', 'charge', 'done', '11', 'RUB', '2019-08-15T16:00:00+0', 'yataxi', 'yandex_uid_1'),
  ('event_id_6', 'order_id_1', 'withdraw', 'new', '11', 'RUB', '2019-08-15T15:00:00+0', 'yataxi', 'yandex_uid_1');

INSERT INTO cashback.events
  (id, external_ref, type, status, value, currency, created, service, yandex_uid, payload)
VALUES
  ('event_id_7', 'order_id_4', 'withdraw', 'new', '11', 'RUB', '2019-08-15T15:00:00+0', 'yataxi', 'yandex_uid_1', '{"eda": {"currency": "RUB"}}'),
  ('event_id_8', 'order_id_5', 'withdraw', 'new', '11', 'RUB', '2019-08-15T15:00:00+0', 'yataxi', 'yandex_uid_2', '{"lavka": {"currency": "RUB"}}'),
  ('event_id_9', 'order_id_6', 'withdraw', 'new', '11', 'RUB', '2019-08-15T15:00:00+0', 'yataxi', 'yandex_uid_3', '{"uber": {"currency": "RUB"}}');


INSERT INTO cashback.order_clears
    (order_id, service, value, currency, version, cashback_sum)
VALUES
    ('order_id_11', 'yataxi', '100', 'RUB', 0, '20'),  -- charge / withdraw
    ('order_id_12', 'yataxi', '1000', 'RUB', 1, '200');  -- races


INSERT INTO cashback.order_rates
    (order_id, rates)
VALUES
    ('order_id_default', '{"by_classes": [{"class": "econom", "value": 0.5}]}'),  -- default rate
    ('order_id_with_limit', '{"by_classes": [{"class": "econom", "value": 0.5, "max_absolute_value": 40.0}]}'),  -- rate with limit
    ('order_id_with_marketing_cashback', '{"by_classes": [{"class": "econom", "value": 0.5}], "marketing_cashback": {"possible_cashback": {"value": 0.1}}}'),  -- rate with marketing_cashback
    ('order_id_with_marketing_cashback_with_limit', '{"by_classes": [{"class": "econom", "value": 0.5}], "marketing_cashback": {"possible_cashback": {"value": 0.1, "max_absolute_value": 100}}}');  -- rate with marketing_cashback with limit
