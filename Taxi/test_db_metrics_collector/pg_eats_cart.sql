INSERT INTO
    eats_cart.carts(id, eater_id, place_id, place_slug, place_business, shipping_type, revision, created_at, deleted_at)
VALUES
('00000000000000000000000000000000', '1', '1', 'place_1', 'restaurant', 'delivery', 5, '2021-04-03T01:12:31+03:00', NULL),
('00000000000000000000000000000001', '2', '2', 'place_2', 'restaurant', 'delivery', 6, NOW() - INTERVAL '10 HOUR', NULL),
('00000000000000000000000000000002', '3', '3', 'place_3', 'restaurant', 'delivery', 7, '2021-04-03T01:12:31+03:00', '2021-07-15T11:20:00Z');

INSERT INTO eats_cart.cart_items (cart_id, place_menu_item_id,
                                  price, promo_price, quantity, created_at, deleted_at)
VALUES ('00000000000000000000000000000000', '232323',
        1, NULL, 1, '2021-04-03T01:12:31+03:00', NULL),
       ('00000000000000000000000000000001', '232323',
        1, NULL, 1, '2021-04-03T01:12:31+03:00', '2021-07-15T11:20:00Z'),
       ('00000000000000000000000000000002', '232323',
        1, NULL, 1, '2021-04-03T01:12:31+03:00', NULL);

INSERT INTO eats_cart.eater_cart (eater_id, cart_id, offer_id)
VALUES ('1', '00000000000000000000000000000000', 'offer1'),
       ('2', '00000000000000000000000000000001', 'offer2'),
       ('3', '00000000000000000000000000000002', 'offer3')
ON CONFLICT DO NOTHING;
