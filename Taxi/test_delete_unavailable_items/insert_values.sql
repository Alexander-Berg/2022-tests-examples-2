INSERT INTO eats_cart.carts
(id, eater_id, place_id, place_slug, place_business, shipping_type, revision)
VALUES
('00000000000000000000000000000000', 'eater2', '123', 'place123', 'restaurant', 'delivery', 1);

INSERT INTO eats_cart.eater_cart
(eater_id, cart_id)
VALUES
('eater2', '00000000000000000000000000000000');

INSERT INTO eats_cart.cart_items
(cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
('00000000000000000000000000000000', '123', 100, NULL, 1), -- all, available
('00000000000000000000000000000000', '1234', 100, NULL, 1), -- pickup, available
('00000000000000000000000000000000', '12345', 100, NULL, 1), -- all, available, with promo
('00000000000000000000000000000000', '123456', 100, NULL, 1), -- delivery, available
('00000000000000000000000000000000', '1234567', 100, NULL, 1), -- all, unavailable
('00000000000000000000000000000000', '12345678', 100, NULL, 1), -- delivery, unavailable
('00000000000000000000000000000000', '123456789', 100, NULL, 1); -- pickup, unavailable

INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES ('00000000000000000000000000000000', 'service_fee', 0);


INSERT INTO eats_cart.cart_discounts
(cart_id, promo_id, name, type, description, discount, picture_uri, quantity)
VALUES
('00000000000000000000000000000000', '3', 'old_promo', 'discount', 'old_promo', 100, 'old_promo', 1);


INSERT INTO eats_cart.cart_item_discounts
(cart_item_id, promo_id, promo_type_id, name, picture_uri)
VALUES
('3', '3', '1', 'old_promo', 'old_promo')
