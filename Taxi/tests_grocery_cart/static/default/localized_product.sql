INSERT INTO cart.carts (
    cart_id, cart_version, user_type, user_id, session, bound_sessions, updated,
    created, order_id, status
)
VALUES (
           '11111111-2222-aaaa-bbbb-cccdddeee005', 1,
           'eats_user_id', '12345', 'eats:123', array['taxi:1234']::TEXT[], CURRENT_TIMESTAMP,
           CURRENT_TIMESTAMP - interval '1 hour', '111-exists', 'editing'
       );

INSERT INTO cart.cart_items (
    cart_id, item_id, price, quantity, currency, updated, created
)
VALUES (
           '11111111-2222-aaaa-bbbb-cccdddeee005', 'localized_product', '345', 1, 'RUB',
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
       );
