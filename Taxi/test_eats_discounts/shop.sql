INSERT INTO eats_cart.carts
(id, eater_id, place_id, place_slug, place_business, shipping_type, created_at, promo_subtotal, total, delivery_fee)
VALUES
('00000000000000000000000000000001', 'eater2', '123', 'place123', 'shop', 'delivery', '2021-04-03T01:12:20+03:00', 216, 236.00, 20);

INSERT INTO eats_cart.eater_cart (eater_id, cart_id)
VALUES ('eater2', '00000000000000000000000000000001');

INSERT INTO eats_cart.cart_items (id, cart_id, place_menu_item_id, public_id, price, promo_price, quantity)
VALUES (10, '00000000000000000000000000000001', '21', 'tomato_red_super', 50, null, 1),
       (20, '00000000000000000000000000000001', '2', 'amazing_plov', 40.00, 23.00, 2),
       (30, '00000000000000000000000000000001', '1', 'burger_omega', 70.00, NULL, 2),
       (40, '00000000000000000000000000000001', '1', 'burger_omega', 70.00, NULL, 1);


INSERT INTO eats_cart.new_cart_item_discounts(cart_item_id, promo_id, promo_type_id, name, description, picture_uri, amount, provider)
VALUES (10, '234', '100', 'money_promo', 'Описание', 'some_uri', 20.0, 'own'),
       (40, '23', '103', 'product_promo', 'Описание', 'some_uri', 70.0, 'own');
