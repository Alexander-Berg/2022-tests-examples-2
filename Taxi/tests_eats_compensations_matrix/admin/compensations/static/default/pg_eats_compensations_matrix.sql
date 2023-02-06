INSERT INTO eats_compensations_matrix.compensation_matrices (
    version_code,
    parent_version_code,
    approved_at,
    author,
    approve_author,
    created_at,
    updated_at
)
VALUES
(
    'v.1.0',
    '',
    '2020-06-09T11:00:00+00:00',
    'nevladov',
    'nevladov',
    '2020-06-09T10:00:00+00:00',
    '2020-06-09T09:00:00+00:00'
),
(
    'v.2.0',
    'v.1.0',
    NULL,
    'nevladov',
    NULL,
    '2020-06-09T10:00:00+00:00',
    '2020-06-09T09:00:00+00:00'
),
(
    'v.3.0',
    'v.1.0',
    '2020-06-09T11:00:00+00:00',
    'nevladov',
    'nevladov',
    '2020-06-09T10:00:00+00:00',
    '2020-06-09T09:00:00+00:00'
),
(
    'v.4.0',
    'v.1.0',
    NULL,
    'nevladov',
    NULL,
    '2020-06-09T10:00:00+00:00',
    '2020-06-09T09:00:00+00:00'
);

INSERT INTO eats_compensations_matrix.situation_groups (
    title,
    description,
    priority,
    created_at,
    updated_at
)
VALUES (
    'Долгое ожидание доставки',
    'Долгое ожидание доставки',
    100,
    '2020-06-16T07:00:00+00:00',
    '2020-06-16T17:00:00+00:00'
),
(
    'Проблема с приготовлением еды',
    'Проблема с приготовлением еды',
    99,
    '2020-06-16T07:00:00+00:00',
    '2020-06-16T17:00:00+00:00'
),
(
    'Проблема с приготовлением еды',
    'Проблема с приготовлением еды',
    98,
    '2020-06-16T07:00:00+00:00',
    '2020-06-16T17:00:00+00:00'
);

INSERT INTO eats_compensations_matrix.situations (
    matrix_id,
    group_id,
    code,
    title,
    violation_level,
    responsible,
    need_confirmation,
    priority,
    is_system,
    order_type,
    order_delivery_type,
    created_at,
    updated_at,
    is_available_before_final_status
)
VALUES
(1, 1, 'small_delay', '<= 15 мин', 'low', 'company', false, 100, false, 3, 3, now(), now(), false),
(1, 2, 'medium_delay', 'Более 15 мин', 'low', 'company', false, 99, false, 3, 3, now(), now(), false),
(2, 2, 'long_delay', 'более 30 минут', 'low', 'company', false, 98, false, 3, 7, now(), now(), false),
(2, 2, 'long_delay', 'более 30 минут', 'low', 'company', false, 98, true, 3, 7, now(), now(), false),
(4, 2, 'long_delay', 'более 30 минут', 'low', 'company', false, 98, false, 3, 7, now(), now(), true);

INSERT INTO eats_compensations_matrix.compensation_types (
    type,
    rate,
    description,
    full_refund,
    max_value,
    min_value,
    notification,
    created_at,
    updated_at
)
VALUES
('promocode', 10, null, false, null, null, 'order.compensation.cancel.courier.card', now(), now()),
('promocode', 10, null, false, null, null, 'order.compensation.cancel.courier.cash', now(), now()),
('promocode', 10, null, false, null, null, 'order.compensation.cancel.place.card', now(), now()),
('promocode', 10, null, false, null, null, 'order.compensation.cancel.place.card', now(), now()),
('promocode', 42.1, null, true, null, null, 'order.compensation.refund', now(), now()),
('promocode', 42.9, null, true, null, null, 'order.compensation.tips_refund', now(), now());

INSERT INTO eats_compensations_matrix.compensation_packs (
    situation_id,
    available_source,
    max_cost,
    min_cost,
    compensations_count,
    payment_method_type,
    antifraud_score,
    country,
    delivery_class,
    created_at,
    updated_at
)
VALUES
(1, 15, null, null, 0, 'all', 'all', 'all', 15, '2020-06-16T12:00:00+00:00', '2020-06-16T12:00:00+00:00'),
(1, 6, null, null, 0, 'card', 'all', 'all', 12, '2020-06-16T12:00:00+00:00', '2020-06-16T12:00:00+00:00'),
(2, 6, null, null, 0, 'card', 'all', 'all', 9, '2020-06-16T12:00:00+00:00', '2020-06-16T12:00:00+00:00'),
(3, 1, null, null, 0, 'card', 'all', 'all', 2, '2020-06-16T12:00:00+00:00', '2020-06-16T12:00:00+00:00'),
(3, 1, null, null, 0, 'card', 'all', 'all', 0, '2020-06-16T12:00:00+00:00', '2020-06-16T12:00:00+00:00');

INSERT INTO eats_compensations_matrix.compensation_packs_to_types (
    pack_id,
    type_id
)
VALUES (1, 1), (2, 3), (3, 1), (3, 2), (4, 2);
