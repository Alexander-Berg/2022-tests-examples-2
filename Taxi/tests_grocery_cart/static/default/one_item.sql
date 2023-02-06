INSERT INTO cart.carts (
    cart_id, cart_version, user_type, user_id, session, bound_sessions, updated,
    created, yandex_uid
    )
VALUES (
    '11111111-2222-aaaa-bbbb-cccdddeee001', 1,
    'eats_user_id', '12345', 'eats:123', array['taxi:1234']::TEXT[], CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP - interval '1 hour', 'some_other_uid'
    );

INSERT INTO cart.carts (
    cart_id, cart_version, user_type, user_id, session, bound_sessions, updated,
    created, yandex_uid
)
VALUES (
    '11111111-2222-aaaa-bbbb-cccdddeee004', 1,
    'eats_user_id', '12345', 'eats:123', array['taxi:1234']::TEXT[], CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP - interval '2 hour', 'some_other_uid'
    );

INSERT INTO cart.carts (
    cart_id, cart_version, user_type, user_id, session, bound_sessions, updated,
    created, yandex_uid
    )
VALUES (
    '11111111-2222-aaaa-bbbb-cccdddeee002', 1,
    'yandex_taxi', '1234', 'taxi:1234', array['eats:123']::TEXT[], CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
    'some_uid'
    );


INSERT INTO cart.cart_items (
    cart_id, item_id, price, quantity, currency, updated, created
    )
VALUES (
    '11111111-2222-aaaa-bbbb-cccdddeee001', 'item_id_1', '345', 1, 'RUB',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );

INSERT INTO cart.cart_items (
    cart_id, item_id, price, quantity, currency, updated, created
    )
VALUES (
    '11111111-2222-aaaa-bbbb-cccdddeee002', 'item_id_2', '345', 1, 'RUB',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );
