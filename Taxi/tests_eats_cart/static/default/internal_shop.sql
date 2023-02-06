INSERT INTO eats_cart.carts
(id, eater_id, place_id, place_slug, place_business, shipping_type, created_at, promo_subtotal, total, delivery_fee)
VALUES
('00000000000000000000000000000001', 'eater2', '123', 'place123', 'shop', 'delivery', '2021-04-03T01:12:20+03:00', 123, 143.00, 20);

INSERT INTO eats_cart.eater_cart (eater_id, cart_id)
VALUES ('eater2', '00000000000000000000000000000001');

INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES ('00000000000000000000000000000001', 'service_fee', 0),
       ('00000000000000000000000000000001', 'delivery_fee', 20);

INSERT INTO eats_cart.cart_items (id, cart_id, place_menu_item_id, public_id, price, promo_price, quantity)
VALUES (1, '00000000000000000000000000000001', '232323', 'set_plov', 50, 40, 1),
       (2, '00000000000000000000000000000001', '2', 'amazing_plov', 40.00, NULL, 2),
       (3, '00000000000000000000000000000001', '2', 'amazing_plov', 40.00, NULL, 1),
       (4, '00000000000000000000000000000001', '3', 'amazing_partner_plov', 40.00, 23.00, 1);


INSERT INTO eats_cart.new_cart_item_discounts(cart_item_id, promo_id, promo_type_id, name, description, picture_uri, amount, provider)
VALUES (1, '234', '100', 'burger', 'Описание', 'some_uri', 20.0, 'own'),
       (3, '23', '103', 'new_promo', 'Описание', 'some_uri', 40.0, 'own');
