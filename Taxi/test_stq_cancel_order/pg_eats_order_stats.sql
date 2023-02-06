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
('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe'::UUID, 'phone_id', '1', 2, '2021-05-27 18:32:00+03', current_timestamp, '3105', '2021', 'restaurant', 'native'),
('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf'::UUID, 'eater_id', '1', 2, '2021-05-27 18:32:00+03', current_timestamp, '3105', '2021', 'restaurant', 'native'),
('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ccc'::UUID, 'device_id', '1', 2, '2021-05-27 18:32:00+03', current_timestamp, '3105', '2021', 'restaurant', 'native'),
('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2aaa'::UUID, 'card_id', '1', 2, '2021-05-27 18:32:00+03', current_timestamp, '3105', '2021', 'restaurant', 'native'),
('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ec0'::UUID, 'phone_id', '2', 2, '2021-05-27 18:32:00+03', current_timestamp, '3105', '2021', 'restaurant', 'native'),
('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ec1'::UUID, 'eater_id', '2', 2, '2021-05-27 18:32:00+03', current_timestamp, '3105', '2021', 'restaurant', 'native'),
('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ddd'::UUID, 'device_id', '2', 2, '2021-05-27 18:32:00+03', current_timestamp, '3105', '2021', 'restaurant', 'native'),
('a0ba06b1-c9fa-49b9-aa54-5ecd28bd2bbb'::UUID, 'card_id', '2', 2, '2021-05-27 18:32:00+03', current_timestamp, '3105', '2021', 'restaurant', 'native');

INSERT INTO eats_order_stats.processed_orders
(
    identity_type,
    order_id,
    canceled,
    counter,
    created_at
)
VALUES
('phone_id', '300-400', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ec0'::UUID, current_timestamp),
('eater_id', '300-400', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ec1'::UUID, current_timestamp),
('device_id', '300-400', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ddd'::UUID, current_timestamp),
('card_id', '300-400', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2bbb'::UUID, current_timestamp),
('phone_id', '100-200', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe'::UUID, current_timestamp),
('eater_id', '100-200', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf'::UUID, current_timestamp),
('device_id', '100-200', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ccc'::UUID, current_timestamp),
('card_id', '100-200', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2aaa'::UUID, current_timestamp),
('phone_id', '200-300', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ec0'::UUID, '2021-05-31 18:32:00+03'),
('eater_id', '200-300', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ec1'::UUID, '2021-05-31 18:32:00+03'),
('device_id', '200-300', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ddd'::UUID, '2021-05-31 18:32:00+03'),
('card_id', '200-300', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2bbb'::UUID, '2021-05-31 18:32:00+03'),
('phone_id', '000-100', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe'::UUID, '2021-05-31 18:32:00+03'),
('eater_id', '000-100', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf'::UUID, '2021-05-31 18:32:00+03'),
('device_id', '000-100', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ccc'::UUID, '2021-05-31 18:32:00+03'),
('card_id', '000-100', false, 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2aaa'::UUID, '2021-05-31 18:32:00+03');
