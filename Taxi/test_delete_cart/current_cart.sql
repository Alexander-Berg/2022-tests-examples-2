INSERT INTO eats_cart.carts
(id, eater_id, place_id, place_slug, place_business, shipping_type)
VALUES
('00000000000000000000000000000000', 'eater1', '123', 'place1', 'restaurant', 'delivery');

INSERT INTO eats_cart.eater_cart
(eater_id, cart_id)
VALUES
('eater1', '00000000000000000000000000000000');

INSERT INTO eats_cart.cart_items
(id, cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
(1, '00000000000000000000000000000000', 232323, 100, NULL, 1);

INSERT INTO eats_cart.extra_fees  (cart_id, type, amount)
VALUES ('00000000000000000000000000000000', 'service_fee', 0);
