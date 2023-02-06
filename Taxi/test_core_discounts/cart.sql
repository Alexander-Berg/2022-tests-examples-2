INSERT INTO eats_cart.carts
    (id, eater_id, place_id, place_slug, place_business, shipping_type, revision, created_at)
VALUES 
    ('00000000000000000000000000000000', 'eater2', '123', 'place1', 'restaurant', 'delivery', 1, '2021-07-07T15:00:00Z'),
    ('00000000000000000000000000000001', 'eater3', '123', 'place1', 'restaurant', 'delivery', 1, '2021-07-07T15:00:00Z');

INSERT INTO eats_cart.eater_cart
    (eater_id, cart_id)
VALUES
    ('eater2', '00000000000000000000000000000000'),
    ('eater3', '00000000000000000000000000000001');


INSERT INTO eats_cart.cart_items
    (id, cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
    (10, '00000000000000000000000000000000', '232323', 100, NULL, 1),
    (20, '00000000000000000000000000000000', '232323', 0, NULL, 1),
    (30, '00000000000000000000000000000001', '1', 70, 50, 1),
    (40, '00000000000000000000000000000001', '1', 0, 50, 1);


INSERT INTO eats_cart.extra_fees  (cart_id, type, amount)
VALUES 
    ('00000000000000000000000000000000', 'service_fee', 0),
    ('00000000000000000000000000000001', 'service_fee', 0);


INSERT INTO eats_cart.cart_discounts
    (cart_id, promo_id, name, type, description, discount, picture_uri, quantity)
VALUES
    ('00000000000000000000000000000000', '0', 'promo', 'discount_item', 'discount_item', 0, 'picture', 1),
    ('00000000000000000000000000000001', '2', 'promo_2', 'discount_item', 'discount_item_2', 0, 'picture', 1);


INSERT INTO eats_cart.cart_item_discounts
    (cart_item_id, promo_id, promo_type_id, name, picture_uri)
VALUES
    (20, '0', '2', 'promo', 'picture'),
    (40, '1', '2', 'promo_2', 'picture');
