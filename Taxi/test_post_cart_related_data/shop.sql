INSERT INTO eats_cart.carts
(id, eater_id, place_id, place_slug, place_business, shipping_type, created_at, promo_subtotal, total, delivery_fee)
VALUES
('00000000000000000000000000000001', 'shop_eater', '12345', 'place_slug_shop', 'shop', 'delivery', '2021-04-03T01:12:20+03:00', 216, 236.00, 20);

INSERT INTO eats_cart.eater_cart (eater_id, cart_id)
VALUES ('shop_eater', '00000000000000000000000000000001');

INSERT INTO eats_cart.cart_items (id, cart_id, place_menu_item_id, public_id, price, promo_price, quantity)
VALUES (1, '00000000000000000000000000000001', '21', 'tomato_red_super', 50, null, 1),
       (2, '00000000000000000000000000000001', '2', 'amazing_plov', 40.00, 23.00, 2),
       (3, '00000000000000000000000000000001', '1', 'burger_omega', 70.00, NULL, 2),
       (4, '00000000000000000000000000000001', '1', 'burger_omega', 70.00, NULL, 1);


INSERT INTO eats_cart.new_cart_item_discounts(cart_item_id, promo_id, promo_type_id, name, description, picture_uri, amount, provider)
VALUES (1, '234', '100', 'money_promo', 'Описание', 'some_uri', 20.0, 'own'),
       (4, '23', '103', 'product_promo', 'Описание', 'some_uri', 40.0, 'own');

INSERT INTO eats_cart.extra_fees (cart_id, type, amount, payload)
VALUES ('00000000000000000000000000000001', 'delivery_fee', 20, '{"delivery_class": "regular"}')
       ON CONFLICT DO NOTHING;
