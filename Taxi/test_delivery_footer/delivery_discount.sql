INSERT INTO eats_cart.carts (id, revision, eater_id, place_id, place_slug, place_business, promo_subtotal,
                             total, delivery_fee, service_fee, shipping_type, created_at,
                             updated_at)
VALUES ('00000000000000000000000000000001', 2, 'eater_eda_discount', '123', 'place123', 'restaurant', 40, 61.2, 20, 1.2, 'delivery',
        '2021-04-03T01:12:20+03:00', '2021-04-03T01:12:31+03:00'),
       ('00000000000000000000000000000002', 2, 'eater_place_discount', '123', 'place123', 'restaurant', 40, 61.2, 20, 1.2, 'delivery',
        '2021-04-03T01:12:20+03:00', '2021-04-03T01:12:31+03:00'),
        ('00000000000000000000000000000003', 2, 'eater_no_discount', '123', 'place123', 'restaurant', 40, 61.2, 20, 1.2, 'delivery',
        '2021-04-03T01:12:20+03:00', '2021-04-03T01:12:31+03:00')
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.eater_cart (eater_id, cart_id, offer_id)
VALUES ('eater_eda_discount', '00000000000000000000000000000001', 'offer1'),
       ('eater_place_discount', '00000000000000000000000000000002', 'offer2'),
       ('eater_no_discount', '00000000000000000000000000000003', 'offer3')
ON CONFLICT DO NOTHING;

INSERT INTO eats_cart.cart_items (cart_id, place_menu_item_id,
                                  price, promo_price, quantity, created_at)
VALUES  ('00000000000000000000000000000001', '2',
        40, NULL, 1, '2021-04-03T01:12:31+03:00'),
        ('00000000000000000000000000000002', '2',
        40, NULL, 1, '2021-04-03T01:12:31+03:00'),
        ('00000000000000000000000000000003', '2',
        40, NULL, 1, '2021-04-03T01:12:31+03:00')
ON CONFLICT DO NOTHING;


INSERT INTO eats_cart.extra_fees (cart_id, type, amount, payload)
VALUES ('00000000000000000000000000000001', 'service_fee', 1.2, NULL),
       ('00000000000000000000000000000001', 'delivery_fee', 20, '{"eda_discount": {"id": "1591", "amount":"20", "name":"eat_discount", "description":"", "picture_uri":""}, "next_delivery_discount" : {"from_cost" : "0", "value" : "absolute", "amount" : "123"}}'),
       ('00000000000000000000000000000002', 'service_fee', 1.2, NULL),
       ('00000000000000000000000000000002', 'delivery_fee', 20, '{"place_discount": {"id": "1592", "amount":"20", "name":"place_discount", "description":"", "picture_uri":""}}'),
       ('00000000000000000000000000000003', 'service_fee', 1.2, NULL),
       ('00000000000000000000000000000003', 'delivery_fee', 20, '{}')
ON CONFLICT DO NOTHING;
