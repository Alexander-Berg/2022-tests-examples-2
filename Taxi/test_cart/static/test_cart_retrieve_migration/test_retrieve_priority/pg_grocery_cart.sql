-- priority
INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, updated, created, yandex_uid)
VALUES ('11111111-1111-1111-1111-111111111111', 1, 'eats_user_id', '12345', 'eats:11111111111111111111111111111111', array['taxi:z0000000000000000000000000000000']::TEXT[],
        '2020-02-03 16:33:54.827958+03',
        '2020-02-03 16:33:54.827958+03',
        'some_uid');

INSERT INTO cart.carts (cart_id, cart_version, user_type, user_id, session, bound_sessions, updated, created, yandex_uid)
VALUES ('22222222-2222-2222-2222-222222222222', 1, 'yandex_taxi', 'z0000000000000000000000000000000', 'taxi:z0000000000000000000000000000000', array[]::TEXT[],
        '2020-02-04 16:33:54.827958+03',
        '2020-02-04 16:33:54.827958+03',
        '');
