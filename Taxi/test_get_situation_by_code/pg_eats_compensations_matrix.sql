ALTER SEQUENCE eats_compensations_matrix.compensation_matrices_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.compensation_matrices
(id, version_code, parent_version_code, approved_at, author, approve_author, created_at, updated_at)
VALUES
       (1, 'v.test.2', '', now(), 'vasiliy_yudin', 'vasiliy_yudin', now(), now()),
       (2, 'v.unapproved.0', '', null, 'Renat Shaymagsumov', 'Renat Shaymagsumov', now(), now());

SELECT setval('eats_compensations_matrix.compensation_matrices_id_seq', 2);



ALTER SEQUENCE eats_compensations_matrix.situation_groups_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.situation_groups (id, title, description, priority, created_at, updated_at)
VALUES (1, 'Долгое ожидание доставки', 'Долгое ожидание доставки', 100, now(), now());

SELECT setval('eats_compensations_matrix.situation_groups_id_seq', 1);



ALTER SEQUENCE eats_compensations_matrix.situations_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.situations (id, matrix_id, group_id, code, title, violation_level, responsible,
                                                  need_confirmation, priority, is_system, order_type, order_delivery_type, created_at, updated_at,
                                                  is_available_before_final_status)
VALUES
    (1, 1, 1, 'small_delay', '<= 15 мин', 'low', 'company', false, 100, false, 3, 3, now(), now(), false),
    (2, 1, 1, 'retail_delay', '30 мин', 'low', 'company', false, 100, false, 3, 3, now(), now(), true);

SELECT setval('eats_compensations_matrix.situations_id_seq', 2);

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
('refund', 10, null, false, null, null, 'order.compensation.cancel.courier.card', now(), now()),
('superVoucher', 10, null, false, null, null, 'order.compensation.cancel.courier.cash', now(), now());

INSERT INTO eats_compensations_matrix.compensation_packs (
    situation_id,
    available_source,
    max_cost,
    min_cost,
    compensations_count,
    payment_method_type,
    antifraud_score,
    country,
    created_at,
    updated_at
)
VALUES
(1, 15, null, null, 0, 'all', 'all', 'all', '2020-06-16T12:00:00+00:00', '2020-06-16T12:00:00+00:00');

INSERT INTO eats_compensations_matrix.compensation_packs_to_types (
    pack_id,
    type_id
)
VALUES (1, 1), (1, 2);
