INSERT INTO cashback_int_api.orders(
    order_id, yandex_uid, service_id, created_at, updated_at
)
VALUES
('exist_order_id_1', 'yandex_uid_1', 'mango', '2020-02-02T12:00:00+00:00', '2020-02-02T12:00:00+00:00'),
('exist_order_id_1', 'yandex_uid_1', 'some_other_service', '2020-02-02T12:00:00+00:00', '2020-02-02T12:00:00+00:00'),
('exist_order_id_2', 'yandex_uid_1', 'mango', '2020-02-02T12:00:00+00:00', '2020-02-02T12:00:00+00:00'),
('exist_oldest_order_id_1', 'yandex_uid_1', 'mango', '2020-01-02T12:00:00+00:00', '2020-01-02T12:00:00+00:00'),
('exist_oldest_order_id_2', 'yandex_uid_1', 'mango', '2020-01-02T12:00:00+00:00', '2020-01-02T12:00:00+00:00'),
('exist_order_id_4', 'yandex_uid_4', 'mango', '2020-02-02T12:00:00+00:00', '2020-02-02T12:00:00+00:00'),
('exist_order_id_5', 'yandex_uid_5', 'mango', '2020-02-02T12:00:00+00:00', '2020-02-02T12:00:00+00:00'),
('exist_order_id_6', 'yandex_uid_6', 'mango', '2020-02-02T12:00:00+00:00', '2020-02-02T12:00:00+00:00'),
('exist_order_id_7', 'yandex_uid_7', 'mango', '2020-02-01T11:59:00+00:00', '2020-02-01T12:00:00+00:00');
