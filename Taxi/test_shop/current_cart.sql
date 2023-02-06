INSERT INTO eats_cart.carts
    (id, eater_id, place_id, place_slug, place_business, shipping_type, total, promo_subtotal, revision, created_at)
VALUES 
    ('00000000000000000000000000000000', 'eater2', '123', 'place123', 'shop', 'delivery', '100', '100', 1, '2021-10-10T10:00:00Z'),
    ('00000000000000000000000000000001', 'eater3', '123', 'place123', 'shop', 'delivery', '100', '100', 1, '2021-10-10T11:00:00Z'),
    ('00000000000000000000000000000002', 'eater4', '123', 'place123', 'shop', 'delivery', '101', '101', 1, '2021-10-10T11:00:00Z');

INSERT INTO eats_cart.eater_cart
    (eater_id, cart_id)
VALUES
    ('eater2', '00000000000000000000000000000000'),
    ('eater3', '00000000000000000000000000000001'),
    ('eater4', '00000000000000000000000000000002');

INSERT INTO eats_cart.cart_items
    (cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
    ('00000000000000000000000000000000', '1', 100, NULL, 1),
    ('00000000000000000000000000000001', '232323', 100, NULL, 1),
    ('00000000000000000000000000000002', '232323', 100, NULL, 1),
    ('00000000000000000000000000000002', '313131', 1, NULL, 1);
