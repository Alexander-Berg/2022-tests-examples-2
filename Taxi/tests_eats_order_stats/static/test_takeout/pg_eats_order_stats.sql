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
    payment_method,
    takeout
)
VALUES
    ('phone_id', '000000000000000000000001', 1, '2021-05-27 18:32:00+03', '2021-05-31 18:32:00+03', '3105', '2021', 'restaurant', 'native', 'card', FALSE),
    ('phone_id', '000000000000000000000001', 2, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '2705', '3242', 'restaurant', 'native', 'cash', FALSE),
    ('phone_id', '000000000000000000000002', 2, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '2706', '3243', 'restaurant', 'native', 'cash', FALSE),
    ('eater_id', '1', 4, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '4567', '56789', 'grocery', 'native', 'googlepay', FALSE),
    ('eater_id', '2', 2, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '3476', '5873', 'restaurant', 'native', 'applepay', FALSE),
    ('eater_id', '3', 3, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '38434', '374748', 'restaurant', 'native', 'taxi', FALSE),
    ('phone_id', '3456785678678978908903', 8, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'restaurant', 'native', 'card', FALSE),
    ('eater_id', '4', 1, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'restaurant', 'native', 'card', FALSE),
    ('eater_id', '5', 1, '2021-05-28 13:12:00+03', '2021-05-29 14:33:00+03', '98765678', '564829456', 'restaurant', 'native', 'card', TRUE),
    ('eater_id', '5', 1, '2022-05-28 00:00:00+03', '2022-05-29 00:00:00+03', '98765678', '564829456', 'restaurant', 'native', 'card', FALSE),
    ('eater_id', '6', 1, '2021-05-28 13:12:00+03', '2021-05-29 14:34:00+03', '98765678', '564829456', 'restaurant', 'native', 'card', TRUE)
;
