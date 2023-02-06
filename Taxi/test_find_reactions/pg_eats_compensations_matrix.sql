INSERT INTO eats_compensations_matrix.order_cancel_matrices
(id, version_code, parent_version_code, approved_at, author, approve_author, created_at, updated_at)
VALUES
       (1, 'v.1.0', '', now(), 'vasiliy_yudin', 'vasiliy_yudin', now(), now()),
       (2, 'v.cancel.1', '', now(), 'vasiliy_yudin', 'vasiliy_yudin', now(), now()),
       (3, 'v.cancel.2', '', now(), 'vasiliy_yudin', 'vasiliy_yudin', now(), now());

ALTER SEQUENCE eats_compensations_matrix.order_cancel_reason_groups_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.order_cancel_reason_groups
(id, name, code, created_at, updated_at)
VALUES (1, 'Ресторан', 'place', now(), now()),
       (2, 'Клиент', 'client', now(), now()),
       (3, 'Курьер', 'courier', now(), now()),
       (4, 'Сервис', 'service', now(), now()),
       (5, 'Тест', 'test', now(), now()),
       (6, 'Ресторан (сам)', 'place_self', now(), now()),
       (7, 'Клиент (самостоятельно)', 'client.self', now(), now()),
       (8, 'Партнер (Процесс только доставка)', 'partner.self', now(), now());

SELECT setval('eats_compensations_matrix.order_cancel_reason_groups_id_seq', 8);


ALTER SEQUENCE eats_compensations_matrix.order_cancel_reasons_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.order_cancel_reasons
(id, matrix_id, group_id, name, code, priority, type, order_type, order_delivery_type,
 created_at, updated_at, deleted_at, payment_type, allowed_callers, allowed_countries)
VALUES (1, 2, 1, 'Невозможно дозвониться до ресторана', 'place.unable_to_call', 105, 'unknown', 3, 3,
        now(), now(), null, 1, 111, array['1']),
       (2, 3, 2, 'Технические проблемы', 'place.technical_problem', 102, 'unknown', 3, 3,
        now(), now(), null, 1, 111, array['1']),
       (3, 3, 5, 'test reason', 'place.technical_problem3', 102, 'unknown', 3, 3,
        now(), now(), null, 1, 111, array['1']),
       (4, 3, 5, 'test reason', 'place.technical_problem4', 102, 'unknown', 3, 3,
        now(), now(), null, 1, 111, array['1']),
       (5, 3, 5, 'test reason', 'place.technical_problem5', 102, 'unknown', 3, 3,
        now(), now(), null, 1, 111, array['1']),
       (6, 3, 5, 'test reason', 'place.technical_problem6', 102, 'unknown', 3, 3,
        now(), now(), null, 1, 111, array['1']),
       (7, 3, 5, 'test reason', 'place.technical_problem7', 102, 'unknown', 3, 3,
        now(), now(), now(), 1, 111, array['1']);

SELECT setval('eats_compensations_matrix.order_cancel_reason_groups_id_seq', 3);


ALTER SEQUENCE eats_compensations_matrix.order_cancel_reactions_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.order_cancel_reactions
(id, type, payload, created_at, updated_at)
VALUES (1, 'compensation', '{}', now(), now()),
       (2, 'compensation', '{}', now(), now()),
       (3, 'promocode_return', '{}', now(), now());

SELECT setval('eats_compensations_matrix.order_cancel_reactions_id_seq', 3);


INSERT INTO eats_compensations_matrix.order_cancel_reasons_reactions
(reason_id, reaction_id, minimal_cost, minimal_eater_reliability, is_allowed_before_place_confirmed,
 is_allowed_for_fast_cancellation, is_for_vip_only, deleted_at)
VALUES
(1, 1, 100, 'bad', true, true, false, null),
(1, 3, 100, 'other', true, true, false, null),
(2, 3, 100, 'good', true, true, false, null),
(3, 3, 100, 'bad', true, false, false, null),
(4, 3, 100, 'bad', false, true, false, null),
(5, 3, 100, 'bad', true, true, true, null),
(6, 1, 100, 'bad', true, true, false, now()),
(7, 1, 100, 'bad', true, true, false, null);
