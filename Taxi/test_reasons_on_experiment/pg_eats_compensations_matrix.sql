INSERT INTO eats_compensations_matrix.order_cancel_matrices
(id, version_code, parent_version_code, approved_at, author, approve_author, created_at, updated_at)
VALUES
       (1, 'v.1.0', '', now(), 'vasiliy_yudin', 'vasiliy_yudin', now(), now()),
       (2, 'v.cancel.1', '', now(), 'vasiliy_yudin', 'vasiliy_yudin', now(), now()),
       (3, 'v.cancel.2', '', now(), 'vasiliy_yudin', 'vasiliy_yudin', now(), now()),
       (4, 'v.israel.1', '', now(), 'faraday', 'faraday', now(), now());

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
(id, matrix_id, group_id, name, code, priority, type, order_type, order_delivery_type, created_at, updated_at,
 payment_type, allowed_callers, allowed_countries)
VALUES (1, 2, 1, 'Невозможно дозвониться до ресторана', 'place.unable_to_call', 105, 'unknown', 3, 3, now(), now(),
        1, 111, array['ru']),
       (2, 3, 2, 'Технические проблемы', 'place.technical_problem', 102, 'unknown', 3, 3, now(), now(),
        1, 111, array['ru']),
       (3, 2, 1, 'Невозможно дозвониться до ресторана', 'place.unable_to_call', 105, 'unknown', 3, 3, now(), now(),
        1, 111, array['all']),
       (4, 2, 1, 'Невозможно дозвониться до ресторана', 'place.unable_to_call', 105, 'unknown', 3, 3, now(), now(),
        1, 111, array['kz']);

SELECT setval('eats_compensations_matrix.order_cancel_reason_groups_id_seq', 2);
