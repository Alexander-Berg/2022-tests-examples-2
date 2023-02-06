INSERT INTO eats_cart.carts
    (id, eater_id, place_id, place_slug, place_business, shipping_type, revision, promo_subtotal, total)
VALUES 
    ('00000000000000000000000000000000', 'eater1', '123', 'place123', 'restaurant', 'delivery', 1, 51.98, 101.98), -- absolute
    ('00000000000000000000000000000001', 'eater2', '123', 'place123', 'restaurant', 'delivery', 1, 55.78, 105.78), -- percent
    ('00000000000000000000000000000002', 'eater3', '123', 'place123', 'restaurant', 'delivery', 1, 61.98, 111.98), -- product no discount yet
    ('00000000000000000000000000000003', 'eater4', '123', 'place123', 'restaurant', 'delivery', 1, 61.98, 111.98), -- product has discount
    ('00000000000000000000000000000004', 'eater5', '123', 'place123', 'restaurant', 'delivery', 1, 123.96, 143.96); -- product has discount, for decrease

INSERT INTO eats_cart.eater_cart
    (eater_id, cart_id)
VALUES
    ('eater1', '00000000000000000000000000000000'),
    ('eater2', '00000000000000000000000000000001'),
    ('eater3', '00000000000000000000000000000002'),
    ('eater4', '00000000000000000000000000000003'),
    ('eater5', '00000000000000000000000000000004');

INSERT INTO eats_cart.cart_items
    (id, cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
    (1, '00000000000000000000000000000000', '232323', 50, NULL, 1),
    (2, '00000000000000000000000000000001', '232323', 50, NULL, 1),
    (3, '00000000000000000000000000000002', '232323', 50, NULL, 1),
    (4, '00000000000000000000000000000003', '232323', 50, NULL, 1),
    (5, '00000000000000000000000000000003', '232323', 50, NULL, 1),
    (6, '00000000000000000000000000000004', '232323', 50, NULL, 2),
    (7, '00000000000000000000000000000004', '232323', 50, NULL, 2);

SELECT setval('eats_cart.cart_items_id_seq', 8);

INSERT INTO eats_cart.cart_item_options (cart_item_id, option_id, price, promo_price, quantity)
VALUES (1, '1679268432', 3.98, NULL, 1),
       (1, '1679268437', 2, NULL, 1),
       (1, '1679268442', 3, NULL, 2),
       (2, '1679268432', 3.98, NULL, 1),
       (2, '1679268437', 2, NULL, 1),
       (2, '1679268442', 3, NULL, 2),
       (3, '1679268432', 3.98, NULL, 1),
       (3, '1679268437', 2, NULL, 1),
       (3, '1679268442', 3, NULL, 2),
       (4, '1679268432', 3.98, NULL, 1),
       (4, '1679268437', 2, NULL, 1),
       (4, '1679268442', 3, NULL, 2),
       (5, '1679268432', 3.98, NULL, 1),
       (5, '1679268437', 2, NULL, 1),
       (5, '1679268442', 3, NULL, 2),
       (6, '1679268432', 3.98, NULL, 1),
       (6, '1679268437', 2, NULL, 1),
       (6, '1679268442', 3, NULL, 2),
       (7, '1679268432', 3.98, NULL, 1),
       (7, '1679268437', 2, NULL, 1),
       (7, '1679268442', 3, NULL, 2);

INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES
    ('00000000000000000000000000000000', 'delivery_fee', 50),
    ('00000000000000000000000000000001', 'delivery_fee', 50),
    ('00000000000000000000000000000002', 'delivery_fee', 50),
    ('00000000000000000000000000000003', 'delivery_fee', 50),
    ('00000000000000000000000000000004', 'delivery_fee', 20);

INSERT INTO eats_cart.new_cart_item_discounts
    (cart_item_id, promo_id, promo_type_id, name, description, picture_uri, amount, provider)
VALUES
    ('1', '1', '100', 'money_promo_1', 'Описание', 'some_uri', 10, 'place'), -- absolute 10
    ('2', '2', '100', 'money_promo_2', 'Описание', 'some_uri', 6.2, 'place'), -- fraction 10
    ('5', '3', '103', 'product_promo', 'Описание', 'some_uri', 61.98, 'place'), -- product
    ('7', '3', '103', 'product_promo', 'Описание', 'some_uri', 61.98, 'place'); -- product
