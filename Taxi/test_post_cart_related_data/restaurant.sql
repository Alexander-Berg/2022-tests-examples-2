INSERT INTO eats_cart.carts
(id, eater_id, place_id, place_slug, place_business, shipping_type, created_at, promo_subtotal, total, delivery_fee)
VALUES
('00000000000000000000000000000002', 'alco_shop_eater', '12345', 'place_slug_shop', 'restaurant', 'pickup', '2021-04-03T01:12:20+03:00', 216, 236.00, 20);

INSERT INTO eats_cart.eater_cart (eater_id, cart_id)
VALUES ('alco_shop_eater', '00000000000000000000000000000002');

INSERT INTO eats_cart.cart_items (id, cart_id, place_menu_item_id, public_id, price, promo_price, quantity)
VALUES (1, '00000000000000000000000000000002', '21', 'alco_drink_1', 50, null, 1),
       (2, '00000000000000000000000000000002', '2', 'alco_drink_2', 40.00, 23.00, 2);
