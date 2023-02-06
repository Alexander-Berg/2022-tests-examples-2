INSERT INTO eats_misc.notified_orders
(order_nr, notify_type, order_type, subtotal, notified_at)
VALUES
('111-111', 'in_process', 'vip_order', 1000, '2020-02-03T08:00:00.000000Z'),
('222-222', 'in_process', 'big_order', 12000, '2020-02-03T08:00:00.000000Z'),
('333-333', 'in_process', 'big_order', 12000, '2020-02-03T08:00:00.000000Z'),
('444-444', 'in_process', 'big_order', 12000, '2020-02-03T08:00:00.000000Z'),
('555-555', 'in_process', 'big_order', 12000, '2020-02-03T08:00:00.000000Z'),
('666-666', 'in_process', 'big_order', 12000, '2020-02-03T08:00:00.000000Z'),
('777-777', 'in_process', 'vip_order', 2000, '2020-02-03T07:45:00.000000Z'),
('777-777', 'place_unconfirmed_order', 'vip_order', 2000, '2020-02-03T07:45:00.000000Z'),
('888-888', 'in_process', 'vip_order', 4500, '2020-01-03T07:45:00.000000Z');
