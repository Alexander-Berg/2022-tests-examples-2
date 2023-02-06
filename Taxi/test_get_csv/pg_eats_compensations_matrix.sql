
INSERT INTO eats_compensations_matrix.compensation_matrices
(version_code, parent_version_code, approved_at, author, approve_author, created_at, updated_at)
VALUES ('v.1.0', '', now(), 'vasiliy_yudin', 'vasiliy_yudin', now(), now());

ALTER SEQUENCE eats_compensations_matrix.compensation_types_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.compensation_types (id, type, rate, description, full_refund, max_value, min_value, notification, created_at, updated_at)
VALUES (1, 'promocode', 10, null, false, null, null, 'order.compensation.cancel.courier.card', now(), now()),
       (2, 'promocode', 10, null, false, null, null, 'order.compensation.cancel.courier.cash', now(), now()),
       (3, 'promocode', 10, null, false, null, null, 'order.compensation.cancel.place.card', now(), now()),
       (4, 'promocode', 10, null, false, null, null, 'order.compensation.cancel.place.cash', now(), now()),
       (5, 'promocode', 10, null, false, null, null, 'order.compensation.promocode', now(), now()),
       (6, 'promocode', 20, null, false, null, null, 'order.compensation.promocode', now(), now()),
       (7, 'promocode', 30, null, false, null, null, 'order.compensation.promocode', now(), now()),
       (8, 'promocode', 40, null, false, null, null, 'order.compensation.promocode', now(), now()),
       (9, 'promocode', 50, null, false, null, null, 'order.compensation.promocode', now(), now()),
       (10, 'refund', null, null, false, null, 10, 'order.compensation.refund', now(), now()),
       (11, 'refund', null, null, true, null, null, 'order.compensation.refund', now(), now()),
       (12, 'superVoucher', null, null, false, null, null, 'order.compensation.voucher', now(), now()),
       (13, 'tipsRefund', 10.0, 'test', true, 1000, 200, 'order.compensation.tips_refund', now(), now()),
       (14, 'voucher', null, null, false, null, null, 'order.compensation.voucher', now(), now()),
       (15, 'voucher', null, null, true, null, null, 'order.compensation.voucher', now(), now());

SELECT setval('eats_compensations_matrix.compensation_types_id_seq', 15);

ALTER SEQUENCE eats_compensations_matrix.situation_groups_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.situation_groups (id, title, description, priority, created_at, updated_at)
VALUES (1, 'Долгое ожидание доставки', 'Долгое ожидание доставки', 100, now(), now()),
(2, 'Проблема с приготовлением еды', 'Проблема с приготовлением еды', 99, now(), now()),
(3, 'Проблема с качеством еды', 'Проблема с качеством еды', 98, now(), now());

SELECT setval('eats_compensations_matrix.situation_groups_id_seq', 1);


ALTER SEQUENCE eats_compensations_matrix.situations_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.situations (id, matrix_id, group_id, code, title, violation_level, responsible,
                                                  need_confirmation, priority, is_system, order_type, order_delivery_type, created_at, updated_at)
VALUES (1, 1, 1, 'small_delay', '<= 15 мин', 'low', 'company', false, 100, false, 3, 3, now(), now()),
       (2, 1, 2, 'medium_delay', 'Более 15 мин', 'medium', 'company', false, 99, false, 8, 1, now(), now()),
       (3, 1, 3, 'long_delay', 'более 30 минут', 'low', 'place', false, 98, false, 1, 7, now(), now()),
       (4, 1, 3, 'У ситуации нет паков', 'Жаль', 'low', 'place', false, 10, false, 1, 7, now(), now()),
       (5, 1, 3, 'У ситуации в паке нет действий', 'Вот', 'low', 'place', false, 10, false, 1, 7, now(), now());
SELECT setval('eats_compensations_matrix.situations_id_seq', 4);


ALTER SEQUENCE eats_compensations_matrix.compensation_packs_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.compensation_packs
(id, situation_id, available_source, max_cost, min_cost, compensations_count, payment_method_type, antifraud_score, country, delivery_class, created_at, updated_at)
VALUES (1, 1, 15, null, 10, 0, 'all', 'all', 'all', 12, now(), now()),
       (2, 2, 6, 9, null, 0, 'cash', 'good', 'all', 5, now(), now()),
       (3, 3, 6, null, null, 0, 'card', 'all', 'ru', 1, now(), now()),
       (4, 5, 6, null, null, 0, 'card', 'all', 'ru', 4, now(), now())
;
SELECT setval('eats_compensations_matrix.compensation_packs_id_seq', 4);


ALTER SEQUENCE eats_compensations_matrix.compensation_packs_to_types_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.compensation_packs_to_types
(id, pack_id, type_id)
VALUES (1, 1, 5), (2, 2, 14), (3, 2, 10), (4, 3, 10), (5, 3, 13)
;

SELECT setval('eats_compensations_matrix.compensation_packs_to_types_id_seq', 5);
