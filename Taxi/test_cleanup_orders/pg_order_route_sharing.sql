INSERT INTO order_route_sharing.sharing_keys (order_id, sharing_key, finished_at, created_at)
VALUES ('order_1', 'key_1', null, CAST('2020-04-01T10:00:00+03:00' AS TIMESTAMPTZ)),
       ('order_2', 'key_2', CAST('2020-04-04T10:00:00+03:00' AS TIMESTAMPTZ), CAST('2020-04-01T10:00:00+03:00' AS TIMESTAMPTZ)),
       ('order_3', 'key_3', CAST('2020-04-04T09:00:00+03:00' AS TIMESTAMPTZ), CAST('2020-04-01T10:00:00+03:00' AS TIMESTAMPTZ)),
       ('order_4', 'key_4', CAST('2020-04-04T07:00:00+00:00' AS TIMESTAMPTZ), CAST('2020-04-01T10:00:00+03:00' AS TIMESTAMPTZ)),
       ('order_5', 'key_5', CAST('2020-04-04T06:00:00+00:00' AS TIMESTAMPTZ), CAST('2020-04-01T10:00:00+03:00' AS TIMESTAMPTZ)),
       ('order_6', 'key_6', null, CAST('2020-04-04T10:00:00+03:00' AS TIMESTAMPTZ));

INSERT INTO order_route_sharing.phone_ids (sharing_key, phone_id)
VALUES ( 'key_1', '00aaaaaaaaaaaaaaaaaaaa01'),
       ( 'key_1', '00aaaaaaaaaaaaaaaaaaaa02'),
       ( 'key_2', '00aaaaaaaaaaaaaaaaaaaa01');
