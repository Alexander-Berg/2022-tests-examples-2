INSERT INTO order_route_sharing.sharing_keys (order_id, sharing_key, tariff_class, corp_client_id, finished_at)
VALUES ('order_1', 'key_1', null, null, null),
       ('order_2', 'key_2', null, null, CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ)),
       ('order_3', 'key_3', null, null, null),
       ('order_4', 'key_4', null, null, null),
       ('order_5', 'key_5', 'econom', null, null),
       ('order_econom_driving', 'key_6', 'business', null, null),
       ('order_7', 'key_7', null, null, null);

INSERT INTO order_route_sharing.phone_ids (sharing_key, phone_id)
VALUES ( 'key_1', '00aaaaaaaaaaaaaaaaaaaa01'),
       ( 'key_1', '00aaaaaaaaaaaaaaaaaaaa02'),
       ( 'key_2', '00aaaaaaaaaaaaaaaaaaaa01'),
       ( 'key_4', '00aaaaaaaaaaaaaaaaaaaa04'),
       ( 'key_5', '00aaaaaaaaaaaaaaaaaaaa03'),
       ( 'key_6', '00aaaaaaaaaaaaaaaaaaaa06'),
       ( 'key_7', '00aaaaaaaaaaaaaaaaaaaa07');
