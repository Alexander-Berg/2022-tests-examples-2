INSERT INTO eats_cart.carts
    (id, eater_id, place_id, place_slug, place_business, shipping_type, revision, promo_subtotal, total)
VALUES 
    ('00000000000000000000000000000001', 'eater2', '123', 'place123', 'restaurant', 'delivery', 1, 225, 225),
    ('00000000000000000000000000000002', 'eater3', '123', 'place123', 'restaurant', 'delivery', 1, 225, 225), -- failed checker by cart promo
    ('00000000000000000000000000000003', 'eater4', '123', 'place123', 'restaurant', 'delivery', 1, 225, 225); -- failed chcker by gift item

INSERT INTO eats_cart.eater_cart
    (eater_id, cart_id)
VALUES
    ('eater2', '00000000000000000000000000000001'),
    ('eater3', '00000000000000000000000000000002'),
    ('eater4', '00000000000000000000000000000003');

INSERT INTO eats_cart.cart_items
    (id, cart_id, place_menu_item_id, price, promo_price, quantity, dynamic_price_part)
VALUES
    (10, '00000000000000000000000000000001', '232323', 50, NULL, 5, 10),
    (20, '00000000000000000000000000000001', '1', 81, NULL, 3, 11),
    (30, '00000000000000000000000000000002', '232323', 50, NULL, 5, 12),
    (40, '00000000000000000000000000000003', '232323', 50, NULL, 5, 13),
    (50, '00000000000000000000000000000003', '232323', 64, NULL, 1, 14);


INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES
    ('00000000000000000000000000000001', 'delivery_fee', 0),
    ('00000000000000000000000000000002', 'delivery_fee', 0),
    ('00000000000000000000000000000003', 'delivery_fee', 0);

INSERT INTO eats_cart.new_cart_discounts
    (cart_id, promo_id, promo_type_id, name, description, picture_uri, amount, provider)
VALUES
    ('00000000000000000000000000000001', '1111', '104', 'zagolovok', 'podzagolok', '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png', 25, 'place'),
    ('00000000000000000000000000000002', '1', '104', 'old_discount', 'podzagolok', '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png', 25, 'place'); -- old discount


INSERT INTO eats_cart.new_cart_item_discounts
    (cart_item_id, promo_id, promo_type_id, name, description, picture_uri, amount, provider)
VALUES
    ('20', '1111', '105', 'zagolovok', 'podzagolok', '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png', 81, 'place'), -- gift item
    ('50', '2', '105', 'old_discount', 'podzagolok', '/images/3191933/0eefb4db5b04722d7bd9b2ac9bd779f0.png', 64, 'place'); -- old discount gift item
