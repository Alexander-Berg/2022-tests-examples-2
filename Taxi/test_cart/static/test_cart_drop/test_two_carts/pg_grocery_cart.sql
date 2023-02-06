INSERT INTO cart.carts (
    cart_id, cart_version, user_type, user_id, session, status, order_id
    )
VALUES (
    '00000000-0000-0000-0000-000000000001', 1, 'yandex_taxi', '1234', 'taxi:1234', 'editing', '777'
    );

INSERT INTO cart.carts (
    cart_id, cart_version, user_type, user_id, session, status, order_id
    )
VALUES (
    '00000000-0000-0000-0000-000000000002', 1, 'yandex_taxi', '1234', 'taxi:1234', 'editing', '778'
    );

INSERT INTO cart.cart_items (
    cart_id, item_id, price, quantity, currency, updated, created
    )
VALUES (
    '00000000-0000-0000-0000-000000000001', 'item_id_11', '345', 1, 'RUB',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );

INSERT INTO cart.cart_items (
    cart_id, item_id, price, quantity, currency, updated, created
    )
VALUES (
    '00000000-0000-0000-0000-000000000001', 'item_id_12', '345', 1, 'RUB',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );

INSERT INTO cart.cart_items (
    cart_id, item_id, price, quantity, currency, updated, created
    )
VALUES (
    '00000000-0000-0000-0000-000000000002', 'item_id_21', '345', 1, 'RUB',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );

INSERT INTO cart.cart_items (
    cart_id, item_id, price, quantity, currency, updated, created
    )
VALUES (
    '00000000-0000-0000-0000-000000000002', 'item_id_22', '345', 1, 'RUB',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );
