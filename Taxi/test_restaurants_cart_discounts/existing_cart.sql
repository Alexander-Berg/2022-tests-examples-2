INSERT INTO eats_cart.carts
    (id, eater_id, place_id, place_slug, place_business, shipping_type, revision, promo_subtotal, total)
VALUES 
    ('00000000000000000000000000000001', 'eater2', '123', 'place123', 'restaurant', 'delivery', 1, 40, 90),
    ('00000000000000000000000000000002', 'eater3', '123', 'place123', 'restaurant', 'delivery', 1, 100, 150),
    ('00000000000000000000000000000003', 'eater4', '123', 'place123', 'restaurant', 'delivery', 1, 250, 250),
    ('00000000000000000000000000000004', 'eater5', '333', 'place333', 'restaurant', 'delivery', 1, 40, 90),
    ('00000000000000000000000000000005', 'eater6', '123', 'place123', 'restaurant', 'delivery', 1, 170, 220),
    ('00000000000000000000000000000006', 'eater6', '123', 'place123', 'restaurant', 'delivery', 1, 250, 250);

INSERT INTO eats_cart.eater_cart
    (eater_id, cart_id)
VALUES
    ('eater2', '00000000000000000000000000000001'),
    ('eater3', '00000000000000000000000000000002'),
    ('eater4', '00000000000000000000000000000003'),
    ('eater5', '00000000000000000000000000000004'),
    ('eater6', '00000000000000000000000000000005'),
    ('eater7', '00000000000000000000000000000006');

INSERT INTO eats_cart.cart_items
    (id, cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
    (10, '00000000000000000000000000000001', '232323', 50, NULL, 1),
    (20, '00000000000000000000000000000001', '232323', 50, NULL, 1),
    (30, '00000000000000000000000000000002', '232323', 50, NULL, 2),
    (40, '00000000000000000000000000000002', '232323', 50, NULL, 1),
    (50, '00000000000000000000000000000003', '232323', 50, NULL, 5),
    (60, '00000000000000000000000000000003', '1', 70, NULL, 1),
    (70, '00000000000000000000000000000004', '232323', 50, NULL, 1),
    (80, '00000000000000000000000000000005', '232323', 50, NULL, 1),
    (90, '00000000000000000000000000000005', '1', 70, NULL, 2),
    (95, '00000000000000000000000000000006', '232323', 50, NULL, 5),
    (96, '00000000000000000000000000000006', '1', 70, NULL, 3);


INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES
    ('00000000000000000000000000000001', 'delivery_fee', 50),
    ('00000000000000000000000000000002', 'delivery_fee', 50),
    ('00000000000000000000000000000003', 'delivery_fee', 0),
    ('00000000000000000000000000000004', 'delivery_fee', 50),
    ('00000000000000000000000000000005', 'delivery_fee', 50),
    ('00000000000000000000000000000006', 'delivery_fee', 0);

INSERT INTO eats_cart.new_cart_discounts
    (cart_id, promo_id, promo_type_id, name, description, picture_uri, amount, provider)
VALUES
    ('00000000000000000000000000000001', '2', '100', 'old_discount', 'descr', 'picture', 10, 'place'),
    ('00000000000000000000000000000004', '4', '100', 'old_discount', 'descr', 'picture', 10, 'place'),
    ('00000000000000000000000000000005', '8', '100', 'old_discount_2', 'descr', 'picture', 10, 'place'),
    ('00000000000000000000000000000005', '4', '100', 'old_discount', 'descr', 'picture', 10, 'place');



INSERT INTO eats_cart.new_cart_item_discounts
    (cart_item_id, promo_id, promo_type_id, name, description, picture_uri, amount, provider)
VALUES
    ('20', '1', '105', 'name', 'Описание', 'some_uri', 50, 'place'), -- old gift item
    ('40', '1', '103', 'name', 'Описание', 'some_uri', 50, 'place'), -- free item
    ('60', '1111', '105', 'name', 'Описание', 'some_uri', 70, 'place'), -- gift item
    ('96', '1111', '105', 'zagolovok', 'podzagolok', '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png', 70, 'place'); -- gift item
