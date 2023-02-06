INSERT INTO eats_cart.carts
    (id, eater_id, place_id, place_slug, place_business, shipping_type, revision, delivery_time)
VALUES 
    ('00000000000000000000000000000000', 'restaurant_eater', '123', 'place123', 'restaurant', 'delivery', 1, (20,30)),
    ('00000000000000000000000000000001', 'shop_eater', '12345', 'place_slug_shop', 'shop', 'delivery', 1, (20,30));

INSERT INTO eats_cart.eater_cart
    (eater_id, cart_id)
VALUES
    ('restaurant_eater', '00000000000000000000000000000000'),
    ('shop_eater', '00000000000000000000000000000001');

INSERT INTO eats_cart.cart_items
    (cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
    ('00000000000000000000000000000000', '232323', 100, NULL, 1),
    ('00000000000000000000000000000001', '21', 50, NULL, 3);
