INSERT INTO order_route_sharing.sharing_keys (order_id, sharing_key, application, tariff_class, finished_at, created_at)
VALUES ('order_1', 'key_1', 'android', 'econom', null, CAST('2020-04-01T10:00:00+03:00' AS TIMESTAMPTZ)),
       ('order_2', 'key_2', 'android', 'express', null, CAST('2020-04-01T10:00:00+03:00' AS TIMESTAMPTZ)),
       ('order_3', 'key_3', null, null, null, CAST('2020-04-01T10:00:00+03:00' AS TIMESTAMPTZ)),
       ('order_4', 'key_4', 'call_center', 'express', null, CAST('2020-04-01T10:00:00+03:00' AS TIMESTAMPTZ)),
       ('order_5', 'key_5', 'call_center', 'express', CAST('2020-04-04T06:00:00+00:00' AS TIMESTAMPTZ), CAST('2020-04-01T10:00:00+03:00' AS TIMESTAMPTZ)),
       ('order_6', 'key_6', 'call_center', 'express', null, CAST('2020-04-04T10:00:00+03:00' AS TIMESTAMPTZ));

INSERT INTO order_route_sharing.phone_ids (sharing_key, phone_id, is_shown, is_user_exists)
VALUES ( 'key_1', '00aaaaaaaaaaaaaaaaaaaa01', true, true),
       ( 'key_1', '00aaaaaaaaaaaaaaaaaaaa02', true, true),
       ( 'key_2', '00aaaaaaaaaaaaaaaaaaaa01', false, false),
       ( 'key_3', '00aaaaaaaaaaaaaaaaaaaa01', false, false),
       ( 'key_4', '00aaaaaaaaaaaaaaaaaaaa01', false, false),
       ( 'key_5', '00aaaaaaaaaaaaaaaaaaaa01', false, false),
       ( 'key_6', '00aaaaaaaaaaaaaaaaaaaa01', false, false);
