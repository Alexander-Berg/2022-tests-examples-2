INSERT INTO eats_cart.carts (id, revision, eater_id, place_id, place_slug, place_business, promo_subtotal,
                             total, delivery_fee, shipping_type, created_at,
                             updated_at, deleted_at)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', 2, 'eats:007', '123', 'place123', 'restaurant', 1, 56, 55, 'delivery',
        '2021-04-01T11:20:00Z', '2021-04-03T01:12:31+03:00', NULL),
       ('2b73add7-9c84-4440-9d3a-12f3e71c6026', 3, 'eats:1', '123', 'place123', 'restaurant', 1, 56, 55, 'delivery',
        '2021-04-01T11:20:00Z', '2021-04-03T01:12:31+03:00', NULL),
       ('3c73add7-9c84-4440-9d3a-12f3e71c6026', 4, 'eats:test', '123', 'place123', 'restaurant', 1, 56, 55, 'delivery',
        '2021-04-01T11:20:00Z', '2021-04-03T01:12:31+03:00', NULL)
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.eater_cart (eater_id, cart_id, offer_id)
VALUES ('eats:007', '1a73add7-9c84-4440-9d3a-12f3e71c6026', 'offer1'),
       ('eats:1', '2b73add7-9c84-4440-9d3a-12f3e71c6026', 'offer2'),
       ('eats:test', '3c73add7-9c84-4440-9d3a-12f3e71c6026', 'offer3')
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', 'delivery_fee', 55),
       ('2b73add7-9c84-4440-9d3a-12f3e71c6026', 'delivery_fee', 55),
       ('3c73add7-9c84-4440-9d3a-12f3e71c6026', 'delivery_fee', 55);

INSERT INTO eats_cart.cart_items (id, cart_id, place_menu_item_id,
                                  price, promo_price, quantity, created_at)
VALUES (0, '1a73add7-9c84-4440-9d3a-12f3e71c6026', '232323',
        1, NULL, 1, '2021-04-03T01:12:31+03:00'),
       (0, '2b73add7-9c84-4440-9d3a-12f3e71c6026', '232323',
        1, NULL, 1, '2021-04-03T01:12:31+03:00'),
       (0, '3c73add7-9c84-4440-9d3a-12f3e71c6026', '232323',
        1, NULL, 1, '2021-04-03T01:12:31+03:00')
ON CONFLICT DO NOTHING;
