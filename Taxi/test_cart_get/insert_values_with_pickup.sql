INSERT INTO eats_cart.carts (id, revision, eater_id, place_id, place_slug, place_business, promo_subtotal,
                             total, delivery_fee, service_fee, shipping_type, created_at,
                             updated_at, deleted_at)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', 2, 'eater1', '123', 'place123', 'restaurant', 1, 56, 55, 0, 'delivery',
        '2021-04-01T11:20:00Z', '2021-04-03T01:12:31+03:00', NULL),
       ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 0, 'eater2', '123', 'place123', 'restaurant', 142.5, 167.96, 20, 0, 'delivery',
        '2021-04-03T01:12:20+03:00', '2021-04-03T01:12:31+03:00', NULL),
       ('00000000000000000000000000000001', 0, 'eater3', '123', 'place123', 'restaurant', 142.5, 169.01, 20, 1.05, 'delivery',
        '2021-04-03T01:12:25+03:00', '2021-04-03T01:12:36+03:00', NULL),
       ('00000000000000000000000000000002', 0, 'eater4', '123', 'place123', 'restaurant', 97.9, 117.95, 20, 1.05, 'delivery',
        '2021-04-03T01:12:25+03:00', '2021-04-03T01:12:36+03:00', NULL),
        ('00000000000000000000000000000003', 0, 'eater5', '123', 'place123', 'restaurant', 97.9, 117.95, 20, 1.05, 'pickup',
        '2021-04-03T01:12:25+03:00', '2021-04-03T01:12:36+03:00', NULL) 
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.eater_cart (eater_id, cart_id, offer_id)
VALUES ('eater1', '1a73add7-9c84-4440-9d3a-12f3e71c6026', 'offer1'),
       ('eater2', '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 'offer123'),
       ('eater3', '00000000000000000000000000000001', 'offer3'),
       ('eater4', '00000000000000000000000000000002', 'offer3'),
       ('eater5', '00000000000000000000000000000003', 'offer3')
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.cart_items (id, cart_id, place_menu_item_id,
                                  price, promo_price, quantity, created_at)
VALUES (0, '1a73add7-9c84-4440-9d3a-12f3e71c6026', '111',
        1, NULL, 1, '2021-04-03T01:12:31+03:00'),
       (2, '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', '232323',
        50.00, 48.95, 2, '2021-04-03T01:12:31+03:00'),
       (3, '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', '2', 
        40.00, NULL, 1, '2021-04-03T01:12:31+03:00'),
       (4, '00000000000000000000000000000001', '232323',
        50.00, 48.95, 2, '2021-04-03T01:12:31+03:00'),
       (5, '00000000000000000000000000000001', '2',
        40.00, NULL, 1, '2021-04-03T01:12:31+03:00'),
       (6, '00000000000000000000000000000002', '232323',
        50.00, 48.95, 2, '2021-04-03T01:12:31+03:00'),
        (7, '00000000000000000000000000000003', '232323',
        50.00, 48.95, 2, '2021-04-03T01:12:31+03:00')
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.cart_item_options (cart_item_id, option_id, price, promo_price, quantity)
VALUES (2, '1679268432', 3.98, 2.33, 1),
       (2, '1679268442', 0, NULL, 1);


INSERT INTO eats_cart.cart_discounts(cart_id, promo_id, name, type, description, discount, picture_uri, quantity, deleted_at)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', '41', 'name', 'type', 'description', 4.5, 'picture_uri', 1, NULL),
       ('00000000000000000000000000000001', '41', 'name', 'type', 'description', 4.5, 'picture_uri', 1, '2021-04-03T01:12:39+03:00');

INSERT INTO eats_cart.cart_item_discounts(cart_item_id, promo_id, promo_type_id, name, picture_uri)
VALUES (0, '41', '1', 'name', 'picture_uri');

INSERT INTO eats_cart.cart_promocodes (cart_id, code, percent, amount_limit,
                                       amount, code_type, descr)
VALUES ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 'code1', Null, Null, 5,
        'code_type1', '10% off for your first order');

INSERT INTO eats_cart.surge_info (cart_id, surge_level, additional_fee, time_factor, min_order_price)
VALUES ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 2, '20', NULL, NULL);

INSERT INTO eats_cart.extra_fees (cart_id, type, amount, payload)
VALUES ('0fe426b3-96ba-438e-a73a-d2cd70dbe3d9', 'delivery_fee', 20, '{"delivery_time":"2021-04-03T00:00:00+03:00"}'),
       ('00000000000000000000000000000001', 'delivery_fee', 20, '{"delivery_time":"2021-04-03T00:00:00+03:00"}'),
       ('00000000000000000000000000000001', 'service_fee', 1.05, NULL); 
