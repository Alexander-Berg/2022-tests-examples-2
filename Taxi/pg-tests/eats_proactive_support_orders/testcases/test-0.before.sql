INSERT INTO eats_proactive_support.orders
(order_nr, status, promised_at, order_type, delivery_type, shipping_type, payload, updated_at)
VALUES
('100000-100000', 'created', NOW(), 'dummy_order_type',
 'dummy_delivery_type', 'dummy_shipping_type', '{}', '2021-10-12T12:00:00.1234+03:00'::TIMESTAMPTZ),
('100001-100000', 'created', NOW(), 'dummy_order_type',
 'dummy_delivery_type', 'dummy_shipping_type', '{}', '2021-11-12T12:00:00.1234+03:00'::TIMESTAMPTZ),
('100011-100000', 'created', NOW(), 'dummy_order_type',
 'dummy_delivery_type', 'dummy_shipping_type', '{}', '2021-12-01T12:00:00.1234+03:00'::TIMESTAMPTZ),
('100111-100000', 'created', NOW(), 'dummy_order_type',
 'dummy_delivery_type', 'dummy_shipping_type', '{}', '2021-12-12T12:00:00.1234+03:00'::TIMESTAMPTZ);
