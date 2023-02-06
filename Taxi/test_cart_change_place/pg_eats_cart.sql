INSERT INTO eats_cart.carts (id, revision, eater_id, place_id, place_slug, place_business, promo_subtotal,
                             total, delivery_fee, service_fee, shipping_type, created_at,
                             updated_at, deleted_at)
VALUES ('00000000000000000000000000000001', 0, 'eater3', '123', 'place_1', 'shop', 142.5, 169.01, 20, 1.05, 'delivery',
        '2021-04-03T01:12:25+03:00', '2021-04-03T01:12:36+03:00', NULL)
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.eater_cart (eater_id, cart_id, offer_id)
VALUES ('eater3', '00000000000000000000000000000001', 'offer3')
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.cart_items (cart_id,  place_menu_item_id, public_id,
                                  price, promo_price, quantity, created_at)
VALUES ('00000000000000000000000000000001', '1', 'public_id_1',
        50.00, 48.95, 2, '2021-04-03T01:12:31+03:00'),
       ('00000000000000000000000000000001', '2', 'public_id_2',
        40.00, NULL, 2, '2021-04-03T01:12:31+03:00'),
       ('00000000000000000000000000000001', '3', 'public_id_3',
        40.00, NULL, 2, '2021-04-03T01:12:31+03:00'),
       ('00000000000000000000000000000001', '4', 'public_id_4',
        40.00, NULL, 2, '2021-04-03T01:12:31+03:00')
ON CONFLICT DO NOTHING;
