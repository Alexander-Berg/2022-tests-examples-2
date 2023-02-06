INSERT INTO eats_cart.carts (id, revision, eater_id, place_id, place_slug, place_business, promo_subtotal,
                             total, delivery_fee, shipping_type, created_at,
                             updated_at, deleted_at)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', 2, '21', '12', 'place1', 'restaurant', 5000, 5600, 600, 'delivery',
        '2021-04-01T11:20:00Z', '2021-04-03T01:12:31+03:00', NULL);

INSERT INTO eats_cart.eater_cart (eater_id, cart_id, offer_id)
VALUES ('21', '1a73add7-9c84-4440-9d3a-12f3e71c6026', 'offer1');

INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', 'delivery_fee', 600);

INSERT INTO eats_cart.cart_items (cart_id, place_menu_item_id,
                                  price, promo_price, quantity, created_at)
VALUES ('1a73add7-9c84-4440-9d3a-12f3e71c6026', '111',
        1, NULL, 1, '2021-04-03T01:12:31+03:00'),
       ('1a73add7-9c84-4440-9d3a-12f3e71c6026', '232323',
        50.00, 48.95, 2, '2021-04-03T01:12:31+03:00'),
       ('1a73add7-9c84-4440-9d3a-12f3e71c6026', '2', 
        40.00, NULL, 1, '2021-04-03T01:12:31+03:00');
