INSERT INTO eats_cart.carts
    (id, eater_id, place_id, place_slug, place_business, shipping_type, revision, total, promo_subtotal, delivery_fee)
VALUES 
    ('00000000000000000000000000000000', 'eater2', '123', 'place123', 'shop', 'delivery', 1, 3020, 3000, 20),
    ('00000000000000000000000000000001', 'eater1', '123', 'place123', 'restaurant', 'delivery', 1, 3020, 3000, 20);

INSERT INTO eats_cart.eater_cart
    (eater_id, cart_id)
VALUES
    ('eater2', '00000000000000000000000000000000'),
    ('eater1', '00000000000000000000000000000001');

INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES ('00000000000000000000000000000000', 'service_fee', 0),
       ('00000000000000000000000000000001', 'service_fee', 0),
       ('00000000000000000000000000000000', 'delivery_fee', 20),
       ('00000000000000000000000000000001', 'delivery_fee', 20);

INSERT INTO eats_cart.cart_items
    (id, cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
    (1, '00000000000000000000000000000000', '1', 100, NULL, 15),
    (2, '00000000000000000000000000000001', '1', 100, NULL, 15),
    (4, '00000000000000000000000000000001', '1', 100, NULL, 15);

INSERT INTO eats_cart.cart_item_discounts(cart_item_id, promo_id, promo_type_id, name, picture_uri)
VALUES
    (4, '2', '1', 'second_promo', 'second_promo');
