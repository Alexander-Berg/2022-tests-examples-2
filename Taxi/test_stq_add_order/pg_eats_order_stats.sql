INSERT INTO eats_order_stats.orders_counters
(
    identity_type,
    identity_value,
    counter_value,
    first_order_at,
    last_order_at,
    place_id,
    brand_id,
    business_type,
    delivery_type
)
VALUES
('phone_id', '2222', 4, '2021-05-27 18:32:00+03', '2021-05-31 18:32:00+03', '234', '432', 'grocery', 'native'),
('eater_id', '2222', 3, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '234', '432', 'grocery', 'native'),
('phone_id', '999', 1, '2021-05-27 18:32:00+03', '2021-05-31 18:32:00+03', '45678', '56789', 'restaurant', 'native'),
('eater_id', '999', 1, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '45678', '56789', 'restaurant', 'native');

INSERT INTO eats_order_stats.processed_orders
(
    identity_type,
    order_id,
    canceled,
    created_at
)
VALUES
('phone_id', '202106-76563', false, '2021-05-31 18:32:00+03'),
('eater_id', '202106-76563', false, '2021-05-29 14:33:00+03');
