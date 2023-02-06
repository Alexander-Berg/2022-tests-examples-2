INSERT INTO eats_order_stats.orders_counters
(
    id,
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
    ('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe'::UUID, 'phone_id', '1', 2, '2021-05-31 18:32:00+03', '2021-06-02 18:32:00+03', '3105', '2021', 'restaurant', 'native'),
    ('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf'::UUID, 'eater_id', '1', 2, '2021-05-31 18:32:00+03', '2021-06-02 18:32:00+03', '3105', '2021', 'restaurant', 'native');

INSERT INTO eats_order_stats.processed_orders
(
    identity_type,
    order_id,
    canceled,
    counter,
    created_at
)
VALUES
    ('phone_id', '100-200', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe'::UUID, '2021-06-02 18:32:00+03'),
    ('eater_id', '100-200', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf'::UUID, '2021-06-02 18:32:00+03'),
    ('phone_id', '000-100', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe'::UUID, '2021-05-31 18:32:00+03'),
    ('eater_id', '000-100', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf'::UUID, '2021-05-31 18:32:00+03'),
    ('phone_id', '200-300', true, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe'::UUID, '2021-06-06 18:32:00+03'),
    ('eater_id', '200-300', true, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf'::UUID, '2021-06-06 18:32:00+03');

-- same data (except payment_method) in new schema table
INSERT INTO eats_order_stats_v2.orders_counters
(
    id,
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
    ('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe'::UUID, 'phone_id', '1', 2, '2021-05-31 18:32:00+03', '2021-06-02 18:32:00+03', '3105', '2021', 'restaurant', 'native', 'card'),
    ('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf'::UUID, 'eater_id', '1', 2, '2021-05-31 18:32:00+03', '2021-06-02 18:32:00+03', '3105', '2021', 'restaurant', 'native', 'cash');

INSERT INTO eats_order_stats_v2.processed_orders
(
    identity_type,
    order_id,
    canceled,
    counter,
    created_at
)
VALUES
    ('phone_id', '100-200', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe'::UUID, '2021-06-02 18:32:00+03'),
    ('eater_id', '100-200', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf'::UUID, '2021-06-02 18:32:00+03'),
    ('phone_id', '000-100', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe'::UUID, '2021-05-31 18:32:00+03'),
    ('eater_id', '000-100', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf'::UUID, '2021-05-31 18:32:00+03'),
    ('phone_id', '200-300', true, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe'::UUID, '2021-06-06 18:32:00+03'),
    ('eater_id', '200-300', true, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf'::UUID, '2021-06-06 18:32:00+03');
