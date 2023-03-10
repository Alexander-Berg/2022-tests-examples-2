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
('phone_id', '000000000000000000000001', 1, '2021-05-27 18:32:00+03', '2021-05-31 18:32:00+03', '3105', '2021', 'restaurant', 'native'),
('phone_id', '000000000000000000000001', 1, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '2705', '3242', 'restaurant', 'native'),
('eater_id', '3456789', 4, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '4567', '56789', 'grocery', 'native'),
('eater_id', '3456789', 2, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '3476', '5873', 'restaurant', 'native'),
('eater_id', '3456789', 3, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '38434', '374748', 'restaurant', 'native'),
('phone_id', '3456785678678978908903', 8, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'restaurant', 'native'),
('eater_id', '456783987654', 1, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'restaurant', 'native'),
('device_id', 'device123', 1, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'restaurant', 'native'),
('device_id', 'device123', 1, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'shop', 'native'),
('card_id', 'card-xa1aaa11a111a111aaa11a11a', 2, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'restaurant', 'native'),
('card_id', 'card-xa1aaa11a111a111aaa11a11a', 4, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'shop', 'native')
;

INSERT INTO eats_order_stats_v2.orders_counters
(
    identity_type,
    identity_value,
    counter_value,
    first_order_at,
    last_order_at,
    place_id,
    brand_id,
    business_type,
    delivery_type,
    payment_method
)
VALUES
    ('phone_id', '000000000000000000000001', 1, '2021-05-27 18:32:00+03', '2021-05-31 18:32:00+03', '3105', '2021', 'restaurant', 'native', 'card'),
    ('phone_id', '000000000000000000000001', 2, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '2705', '3242', 'restaurant', 'native', 'cash'),
    ('phone_id', '000000000000000000000002', 2, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '2706', '3243', 'restaurant', 'native', 'cash'),
    ('eater_id', '3456789', 4, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '4567', '56789', 'grocery', 'native', 'googlepay'),
    ('eater_id', '3456789', 2, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '3476', '5873', 'restaurant', 'native', 'applepay'),
    ('eater_id', '3456789', 3, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '38434', '374748', 'restaurant', 'native', 'taxi'),
    ('phone_id', '3456785678678978908903', 8, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'restaurant', 'native', 'card'),
    ('eater_id', '456783987654', 1, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'restaurant', 'native', 'card'),
    ('device_id', 'device123', 1, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'restaurant', 'native', 'card'),
    ('device_id', 'device123', 1, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'shop', 'native', 'cash'),
    ('card_id', 'card-xa1aaa11a111a111aaa11a11a', 2, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'restaurant', 'native', 'card'),
    ('card_id', 'card-xa1aaa11a111a111aaa11a11a', 4, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'shop', 'native', 'card')
;
