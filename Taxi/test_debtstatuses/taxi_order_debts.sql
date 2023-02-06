INSERT INTO debts.taxi_order_debts
(order_id, order_info, status, yandex_uid, phone_id, created, updated, value, currency, brand)
VALUES ('order_id_1', '{}', 'debt', 'yandex_uid_same_currency', 'phone_id_same_currency', '2022-01-01T00:00:00.0Z', '2022-01-01T00:00:00.0Z', 300, 'RUB', 'yataxi'),
       ('order_id_2', '{}', 'debt', 'yandex_uid_same_currency', 'phone_id_same_currency', '2022-01-02T00:00:00.0Z', '2022-01-02T00:00:00.0Z', 400, 'RUB', 'yataxi'),
       ('order_id_3', '{}', 'debt', 'yandex_uid_same_currency', 'phone_id_same_currency', '2022-01-03T00:00:00.0Z', '2022-01-03T00:00:00.0Z', 150, 'RUB', 'yataxi');

INSERT INTO debts.taxi_order_debts
(order_id, order_info, status, yandex_uid, phone_id, created, updated, value, currency, brand)
VALUES ('order_id_4', '{}', 'debt', 'yandex_uid_diff_currency', 'phone_id_diff_currency', '2022-01-01T00:00:00.0Z', '2022-01-01T00:00:00.0Z', 300, 'RUB', 'yataxi'),
       ('order_id_5', '{}', 'debt', 'yandex_uid_diff_currency', 'phone_id_diff_currency', '2022-01-02T00:00:00.0Z', '2022-01-02T00:00:00.0Z', 40, 'USD', 'yataxi');

