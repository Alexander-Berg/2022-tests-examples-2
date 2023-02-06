INSERT INTO
    eats_cart.carts(id, eater_id, place_id, place_slug, place_business, shipping_type, revision, updated_at)
VALUES 
    ('00000000000000000000000000000000', '1', '1', 'place_1', 'restaurant', 'delivery', 5, '2021-04-01T00:00:00+03:00'),
    ('00000000000000000000000000000001', '2', '2', 'place_2', 'restaurant', 'delivery', 6, '2021-04-01T00:00:00+03:00');

INSERT INTO
    eats_cart.eater_cart(eater_id, cart_id)
VALUES
    ('1', '00000000000000000000000000000000'),
    ('3', NULL);
