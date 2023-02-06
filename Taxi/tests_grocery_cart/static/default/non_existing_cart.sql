INSERT INTO cart.carts (
    cart_id, cart_version, user_type, user_id, session, bound_sessions, updated,
    created
    )
VALUES (
    '11111111-2222-aaaa-bbbb-cccdddeee001', 1,
    'eats_user_id', '12345', 'eats:123', array[]::TEXT[], CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );

INSERT INTO cart.carts (
    cart_id, cart_version, user_type, user_id, session, bound_sessions, updated,
    created
    )
VALUES (
    '11111111-2222-aaaa-bbbb-cccdddeee002', 1,
    'yandex_taxi', '1234', 'taxi:1234', array[]::TEXT[], CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );

INSERT INTO cart.carts (
    cart_id, cart_version, user_type, user_id, session, bound_sessions, updated,
    created, order_id, status
    )
VALUES (
    '11111111-2222-aaaa-bbbb-cccdddeee011', 1,
    'eats_user_id', '12345', 'eats:123', array['taxi:1234']::TEXT[], CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '777', 'checked_out'
    );

INSERT INTO cart.carts (
    cart_id, cart_version, user_type, user_id, session, bound_sessions, updated,
    created, order_id, status
    )
VALUES (
    '11111111-2222-aaaa-bbbb-cccdddeee012', 1,
    'yandex_taxi', '1234', 'taxi:1234', array['eats:123']::TEXT[], CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '778', 'checked_out'
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

INSERT INTO cart.cart_items (
    cart_id, item_id, price, quantity, currency, updated, created
    )
VALUES (
    '11111111-2222-aaaa-bbbb-cccdddeee011', 'item_id_11', '345', 1, 'RUB',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );

INSERT INTO cart.cart_items (
    cart_id, item_id, price, quantity, currency, updated, created
    )
VALUES (
    '11111111-2222-aaaa-bbbb-cccdddeee012', 'item_id_12', '345', 1, 'RUB',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );
