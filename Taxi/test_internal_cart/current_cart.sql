INSERT INTO eats_cart.carts
(id, eater_id, place_id, place_slug, place_business, shipping_type)
VALUES
('00000000000000000000000000000000', 'eater2', '123', 'place1', 'restaurant', 'delivery'),
('00000000000000000000000000000001', 'eater3', '123', 'place1', 'restaurant', 'pickup');

INSERT INTO eats_cart.eater_cart
(eater_id, cart_id)
VALUES
('eater2', '00000000000000000000000000000000'),
('eater3', '00000000000000000000000000000001');

INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES ('00000000000000000000000000000001', 'service_fee', 0),
       ('00000000000000000000000000000001', 'delivery_fee', 0),
       ('00000000000000000000000000000000', 'service_fee', 0),
       ('00000000000000000000000000000000', 'delivery_fee', 0);

INSERT INTO eats_cart.cart_items
(cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
('00000000000000000000000000000000', 232323, 100, NULL, 1),
('00000000000000000000000000000001', 232323, 100, NULL, 1);

