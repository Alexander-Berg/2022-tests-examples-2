INSERT INTO
    eats_cart.carts(id, eater_id, place_id, place_slug, place_business, shipping_type, revision, promo_subtotal, total, delivery_fee)
VALUES 
    ('00000000000000000000000000000000', '1', '2', 'place_2', 'restaurant', 'delivery', 5, 115, 135, 20),
    ('00000000000000000000000000000001', '2', '2', 'place_2', 'restaurant', 'delivery', 6, 115, 135, 20),
    ('00000000000000000000000000000002', '3', '2', 'place_2', 'restaurant', 'delivery', 7, 115, 135, 20);

INSERT INTO
    eats_cart.eater_cart(eater_id, cart_id)
VALUES
    ('1', '00000000000000000000000000000000'),
    ('2', '00000000000000000000000000000001'),
    ('3', '00000000000000000000000000000002');

INSERT INTO eats_cart.cart_items (cart_id, place_menu_item_id,
                                  price, promo_price, quantity, created_at)
VALUES ('00000000000000000000000000000000', '232323',
        115, NULL, 1, '2021-04-03T01:12:31+03:00'),
       ('00000000000000000000000000000001', '232323',
        115, NULL, 1, '2021-04-03T01:12:31+03:00'),
       ('00000000000000000000000000000002', '232323',
        135, 115, 1, '2021-04-03T01:12:31+03:00')
ON CONFLICT DO NOTHING;

INSERT INTO
    eats_cart.cart_promocodes(
        cart_id,
        code,
        percent,
        amount_limit,
        amount,
        code_type,
        descr
    )
VALUES
    ('00000000000000000000000000000000', 'old_code', 10, 100, NULL, 'percent', ''),
    ('00000000000000000000000000000002', 'old_code', 10, 100, NULL, 'percent', '');
