INSERT INTO eats_cart.carts (id, revision, eater_id, place_id, place_slug, place_business, promo_subtotal,
                             total, delivery_fee, service_fee, shipping_type, created_at,
                             updated_at, deleted_at)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', 2, 'eater1', '123', 'place123', 'restaurant', 1, 68.78, 55, 12.78, 'delivery',
        '2021-04-01T11:20:00Z', '2021-04-03T01:12:31+03:00', NULL)
    ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.eater_cart (eater_id, cart_id, offer_id)
VALUES ('eater1', '1a73add7-9c84-4440-9d3a-12f3e71c6026', 'offer1')
    ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', 'service_fee', 12.78),
       ('1a73add7-9c84-4440-9d3a-12f3e71c6026', 'delivery_fee', 55);

INSERT INTO eats_cart.cart_items (id, cart_id, place_menu_item_id,
                                  price, promo_price, quantity, created_at)
VALUES (1, '1a73add7-9c84-4440-9d3a-12f3e71c6026', '232323',
        1, NULL, 1, '2021-04-03T01:12:31+03:00'),
       (0, '1a73add7-9c84-4440-9d3a-12f3e71c6026', '232323',
        0, NULL, 1, '2021-04-03T01:12:31+03:00')
    ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.cart_discounts(cart_id, promo_id, name, type, description, discount, picture_uri, quantity)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', '41', 'name', 'type', 'description', 4.5, 'picture_uri', 1);

INSERT INTO eats_cart.cart_item_discounts(cart_item_id, promo_id, promo_type_id, name, picture_uri)
VALUES (0, '41', '1', 'name', 'picture_uri');

INSERT INTO eats_cart.surge_info (cart_id, surge_level, additional_fee, time_factor, min_order_price)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', 2, '20', NULL, NULL);

INSERT INTO eats_cart.cart_promocodes (cart_id, code, percent, amount_limit,
                                       amount, code_type, descr)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', 'code1', Null, Null, 5,
        'code_type1', '10% off for your first order');
