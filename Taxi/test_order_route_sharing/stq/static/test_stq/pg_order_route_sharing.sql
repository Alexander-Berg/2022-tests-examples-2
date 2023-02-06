INSERT INTO order_route_sharing.sharing_keys (order_id, sharing_key, finished_at)
VALUES ('order_1', 'key_1', null),
       ('order_2', 'key_2', CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ)),
       ('order_3', 'key_3', null),
       ('order_4', 'key_4', null);

INSERT INTO order_route_sharing.phone_ids (sharing_key, phone_id)
VALUES ( 'key_1', '00aaaaaaaaaaaaaaaaaaaa01'),
       ( 'key_1', '00aaaaaaaaaaaaaaaaaaaa02'),
       ( 'key_2', '00aaaaaaaaaaaaaaaaaaaa01');
