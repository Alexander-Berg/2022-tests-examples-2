INSERT INTO eats_cart.carts (id, revision, eater_id, place_id, place_slug, place_business, promo_subtotal,
                             total, delivery_fee, service_fee, shipping_type, created_at,
                             updated_at, deleted_at)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', 2, 'eater1', '123', 'place123', 'restaurant', 1, 56, 55, 0, 'delivery',
        '2021-04-01T11:20:00Z', '2021-04-03T01:12:31+03:00', NULL),
       ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 1, 'eater2', '123', 'place123', 'restaurant', 85.5, 110, 20, 15.1, 'delivery',
        '2021-04-03T01:12:20+03:00', '2021-04-03T01:12:31+03:00', NULL),
       ('00000000000000000000000000000001', 2, 'eater2', '123', 'place123', 'restaurant', 40, 61.2, 20, 1.2, 'delivery',
        '2021-04-03T01:12:20+03:00', '2021-04-03T01:12:31+03:00', '2021-04-03T01:12:35+03:00'),
       ('00000000000000000000000000000000', 1, 'eater2', '123', 'place123', 'restaurant', 0, 0, 0, 0, 'delivery',
        '2021-04-03T01:12:20+03:00', '2021-04-03T01:12:31+03:00', '2021-04-03T01:12:35+03:00') 
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.eater_cart (eater_id, cart_id, offer_id)
VALUES ('eater1', '1a73add7-9c84-4440-9d3a-12f3e71c6026', 'offer1'),
       ('eater2', '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 'offer123')
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.cart_items (id, cart_id, place_menu_item_id,
                                  price, promo_price, quantity, created_at)
VALUES (0, '1a73add7-9c84-4440-9d3a-12f3e71c6026', '111',
        1, NULL, 1, '2021-04-03T01:12:31+03:00'),
       (2, '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', '232323',
        50, NULL, 2, '2021-04-03T01:12:31+03:00'),
       (3, '00000000000000000000000000000001', '2',
        40, NULL, 1, '2021-04-03T01:12:31+03:00')
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.cart_item_options (cart_item_id, option_id, price, promo_price, quantity)
VALUES (2, '1679268432', 4, NULL, 1),
       (2, '1679268442', 0, NULL, 1);

INSERT INTO eats_cart.cart_discounts(cart_id, promo_id, name, type, description, discount, picture_uri, quantity)
VALUES ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', '41', 'name', 'type', 'description', 4.5, 'picture_uri', 3),
       ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', '42', 'name2', 'type2', 'yet another description', 10, 'picture_uri', 2);


INSERT INTO eats_cart.cart_item_discounts(cart_item_id, promo_id, promo_type_id, name, picture_uri)
VALUES (2, '41', '103', 'name', 'picture_uri');

INSERT INTO eats_cart.cart_promocodes (cart_id, code, percent, amount_limit,
                                       amount, code_type, descr)
VALUES ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 'code1', Null, Null, 5,
        'code_type1', '10% off for your first order');

INSERT INTO eats_cart.surge_info (cart_id, surge_level, additional_fee, time_factor, min_order_price)
VALUES ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 1, '10', NULL, NULL);
