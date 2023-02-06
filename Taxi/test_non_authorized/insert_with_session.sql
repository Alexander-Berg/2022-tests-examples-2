INSERT INTO eats_cart.carts (id, revision, eater_id, place_id, place_slug, place_business, promo_subtotal,
                             total, delivery_fee, shipping_type, created_at,
                             updated_at, deleted_at)
VALUES ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 0, 'eats:111', '123', 'place123', 'restaurant', 107.96, 110, 20, 'delivery',
        '2021-04-03T01:12:20+03:00', '2021-04-03T01:12:31+03:00', NULL)
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.eater_cart (eater_id, cart_id, offer_id)
VALUES ('eats:111', '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 'offer123')
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 'delivery_fee', 20);

INSERT INTO eats_cart.cart_items (id, cart_id, place_menu_item_id,
                                  price, promo_price, quantity, created_at)
VALUES (2, '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', '232323',
        50.00, 48.95, 2, '2021-04-03T01:12:31+03:00')
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.cart_item_options (cart_item_id, option_id, price, promo_price, quantity)
VALUES (2, '1679268432', 3.98, 2.33, 1),
       (2, '1679268442', 0, NULL, 1);

INSERT INTO eats_cart.cart_promocodes (cart_id, code, percent, amount_limit,
                                       amount, code_type, descr)
VALUES ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 'code1', Null, Null, 5,
        'code_type1', '10% off for your first order');
