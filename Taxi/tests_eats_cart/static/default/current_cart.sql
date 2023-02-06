INSERT INTO eats_cart.carts
    (id, eater_id, place_id, place_slug, place_business, shipping_type, revision)
VALUES 
    ('00000000000000000000000000000000', 'eater2', '123', 'place123', 'restaurant', 'delivery', 1);

INSERT INTO eats_cart.eater_cart
    (eater_id, cart_id)
VALUES
    ('eater2', '00000000000000000000000000000000');

INSERT INTO eats_cart.cart_items
    (cart_id, place_menu_item_id, price, promo_price, quantity)
VALUES
    ('00000000000000000000000000000000', '1', 100, NULL, 1),
    ('00000000000000000000000000000000', '2', 100, NULL, 1),
    ('00000000000000000000000000000000', '20', 200, NULL, 1);

INSERT INTO eats_cart.extra_fees (cart_id, type, amount)
VALUES ('00000000000000000000000000000000', 'service_fee', 0);


INSERT INTO eats_cart.cart_discounts
    (cart_id, promo_id, name, type, description, discount, picture_uri, quantity)
VALUES
    ('00000000000000000000000000000000', '2', 'second_promo', 'discount', 'second_promo', 100, 'second_promo', 1),
    ('00000000000000000000000000000000', '3', 'old_promo', 'discount', 'old_promo', 100, 'old_promo', 1);


INSERT INTO eats_cart.cart_item_discounts
    (cart_item_id, promo_id, promo_type_id, name, picture_uri)
VALUES
    ('1', '1', '3', 'old_promo', 'old_promo'),
    ('2', '2', '1', 'second_promo', 'second_promo');
