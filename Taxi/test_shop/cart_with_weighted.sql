INSERT INTO eats_cart.carts
    (id, eater_id, place_id, place_slug, place_business, shipping_type, total, promo_subtotal, revision)
VALUES 
    ('00000000000000000000000000000001', 'eater3', '123', 'place123', 'shop', 'delivery', '100', '100', 1);

INSERT INTO eats_cart.eater_cart
    (eater_id, cart_id)
VALUES
    ('eater3', '00000000000000000000000000000001');

INSERT INTO eats_cart.cart_items
    (cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
    ('00000000000000000000000000000001', '232323', 100, NULL, 2),
    ('00000000000000000000000000000001', '2', 100, NULL, 1);
