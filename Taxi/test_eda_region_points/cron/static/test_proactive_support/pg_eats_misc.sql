INSERT INTO eats_misc.notified_orders 
(order_nr, notify_type, order_type, subtotal, notified_at)
VALUES 
('111-111', 'in_process', 'vip_order', 1000, '2020-02-03T07:55:00.000000'::timestamptz),
('222-222', 'in_process', 'big_order', 12000, '2020-01-03T07:45:00.000000'::timestamptz);
