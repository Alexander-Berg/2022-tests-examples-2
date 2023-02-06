INSERT INTO eats_cart.carts
(id, eater_id, place_id, place_slug, place_business, shipping_type, total, promo_subtotal, delivery_fee)
VALUES
('00000000000000000000000000000000', 'eater2', '123', 'place123', 'restaurant', 'delivery', 251.51, 251.51, 0),
('00000000000000000000000000000001', 'eater3', '123', 'place123', 'restaurant', 'delivery', 150, 100, 50);

INSERT INTO eats_cart.eater_cart
(eater_id, cart_id)
VALUES
('eater2', '00000000000000000000000000000000'),
('eater3', '00000000000000000000000000000001');

INSERT INTO eats_cart.extra_fees  (cart_id, type, amount)
VALUES ('00000000000000000000000000000000', 'service_fee', 0),
       ('00000000000000000000000000000001', 'service_fee', 0);

INSERT INTO eats_cart.cart_items
(id, cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
(1, '00000000000000000000000000000000', 123, 50.00, 48.95, 2),
(2, '00000000000000000000000000000000', 123, 50.00, 48.95, 1),
(3, '00000000000000000000000000000000', 1234, 100, NULL, 1),
(6, '00000000000000000000000000000001', 123, 100, NULL, 1);

INSERT INTO eats_cart.cart_item_options (cart_item_id, option_id, price, promo_price, quantity)
VALUES (1, '1679268432', 3.98, 2.33, 1),
       (1, '1679268442', 0, NULL, 1);
