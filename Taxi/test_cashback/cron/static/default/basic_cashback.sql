INSERT INTO cashback.events
  (id, external_ref, type, status, value, currency, created, updated, yandex_uid, source)
VALUES
  ('event_id_1', 'order_id_1', 'invoice', 'new', '50', 'RUB', '2019-08-15T12:00:00+0', '2019-08-15T12:00:00+0', 'yandex_uid', 'user'),
  ('event_id_2', 'order_id_1', 'invoice', 'done', '200', 'RUB', current_timestamp, current_timestamp, 'yandex_uid', 'service'),
  ('event_id_3', 'order_id_1', 'invoice', 'done', '25.3', 'RUB', current_timestamp, current_timestamp, 'yandex_uid', 'user'),
  ('event_id_33', 'order_id_1', 'invoice', 'done', '30', 'EUR', current_timestamp, current_timestamp, 'yandex_uid', 'user'),
  ('event_id_4', 'order_id_2', 'invoice', 'new', '11', 'RUB', current_timestamp, current_timestamp, 'yandex_uid', 'service'),
  ('event_id_5', 'order_id_3', 'invoice', 'failed', '11', 'RUB', current_timestamp, current_timestamp, 'yandex_uid', 'service');


INSERT INTO cashback.order_rates (order_id, rates)
VALUES
('order_id', '{}'::jsonb);

INSERT INTO "cashback"."order_clears"("order_id","value","currency","updated","created","version","cashback_sum")
VALUES
('order_id',467,'RUB',current_timestamp,current_timestamp,1,116);
