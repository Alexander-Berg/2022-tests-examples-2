INSERT INTO debts.taxi_order_debts
(order_id, order_info, status, yandex_uid, phone_id, created, updated, value, currency, brand)
VALUES ('order_id_1', '{}', 'debt', 'yandex_uid_1', 'phone_id_1', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z',
        300, 'RUB', 'yataxi'),
       ('order_id_3', '{}', 'debt', 'yandex_uid_2', 'phone_id_1', current_timestamp, current_timestamp, 40, 'USD', 'yataxi'),
       ('order_id_4', '{}', 'debt', 'yandex_uid_4', 'phone_id_2', current_timestamp, current_timestamp, 15, 'EUR', 'yataxi'),
       ('order_id_5', '{}', 'debt', 'yandex_uid_3', 'phone_id_3', current_timestamp, current_timestamp, 3, 'BTC', 'yataxi');

INSERT INTO debts.taxi_order_debts
(order_id, order_info, status, yandex_uid, phone_id, created, updated, reason_code, brand)
VALUES ('order_id_2', '{}', 'nodebt', 'yandex_uid_2', 'phone_id_2', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z',
        'moved_to_cash', 'yataxi'),
       ('order_id_6', '{}', 'nodebt', 'yandex_uid_5', 'phone_id_4', now(), now(), 'moved_to_cash', 'yataxi');

INSERT INTO debts.taxi_order_debts
(order_id, order_info, status, yandex_uid, phone_id, value, currency, brand)
VALUES  ('order_id_7', '{}', 'debt', 'yandex_uid_123', '555555555555555555555555', 3, 'BTC', 'yataxi2'),
        ('order_id_8', '{}', 'debt', 'yandex_uid_123', '222222222222222222222222', 10, 'BTC', 'yataxi2'),
        ('order_id_9', '{}', 'debt', 'yandex_uid_123', '333333333333333333333333', 23, 'RUB', 'yataxi2'),
        ('order_id_10', '{}', 'debt', 'yandex_uid_123', '777777777777777777777777', 1, 'BTC', 'yataxi2');

INSERT INTO debts.taxi_order_debts
(order_id, order_info, status, yandex_uid, phone_id, created, updated, value, currency, brand)
VALUES ('order_id_11', '{}', 'debt', 'yandex_uid_general_ride_info_same_currency', 'phone_id_general_ride_info_same_currency', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z',
        300, 'RUB', 'yataxi'),
       ('order_id_12', '{}', 'debt', 'yandex_uid_general_ride_info_same_currency', 'phone_id_general_ride_info_same_currency', '2018-12-02T00:00:00.0Z', '2018-12-02T00:00:00.0Z', 400, 'RUB', 'yataxi'),
       ('order_id_13', '{}', 'debt', 'yandex_uid_general_ride_info_same_currency', 'phone_id_general_ride_info_same_currency', '2018-12-03T00:00:00.0Z', '2018-12-03T00:00:00.0Z', 150, 'RUB', 'yataxi');
