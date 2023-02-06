INSERT INTO eats_plus_game.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload)
VALUES
    ('111111-100000', 'created', NOW(), 'dummy_order_type',
     'dummy_delivery_type', 'dummy_shipping_type', '{"eater_personal_phone_id": "+7-777-777-7777"}');
