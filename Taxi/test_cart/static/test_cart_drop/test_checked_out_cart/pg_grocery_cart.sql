INSERT INTO cart.carts (
    cart_id, cart_version, user_type, user_id, session, status, order_id
    )
VALUES (
    '00000000-0000-0000-0000-000000000001', 1, 'yandex_taxi', '1234', 'taxi:12345', 'checked_out', '777'
    );

INSERT INTO cart.cart_items (
    cart_id, item_id, price, quantity, currency, updated, created
    )
VALUES (
    '00000000-0000-0000-0000-000000000001', 'item_id_1', '345', 1, 'RUB',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );
