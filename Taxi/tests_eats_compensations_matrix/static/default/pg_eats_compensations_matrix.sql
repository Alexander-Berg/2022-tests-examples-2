START TRANSACTION;

-- compensation matrix

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
       (10, 'refund', null, null, false, null, null, 'order.compensation.refund', now(), now()),
       (11, 'refund', null, null, true, null, null, 'order.compensation.refund', now(), now()),
       (12, 'superVoucher', null, null, false, null, null, 'order.compensation.voucher', now(), now()),
       (13, 'tipsRefund', null, null, true, null, null, 'order.compensation.tips_refund', now(), now()),
       (14, 'voucher', null, null, false, null, null, 'order.compensation.voucher', now(), now()),
       (15, 'voucher', null, null, true, null, null, 'order.compensation.voucher', now(), now());

SELECT setval('eats_compensations_matrix.compensation_types_id_seq', 15);

ALTER SEQUENCE eats_compensations_matrix.situation_groups_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.situation_groups (id, title, description, priority, created_at, updated_at)
VALUES (1, 'Долгое ожидание доставки', 'Долгое ожидание доставки', 100, now(), now()),
       (2, 'Проблема с приготовлением еды', 'Проблема с приготовлением еды', 99, now(), now()),
       (3, 'Проблема с качеством еды', 'Проблема с качеством еды', 98, now(), now()),
       (4, 'Не учтен комментарий клиента', 'Не учтен комментарий клиента', 97, now(), now()),
       (5, 'Заказ поврежден', 'Заказ поврежден', 96, now(), now()),
       (6, 'Нет соусов или специй', 'Нет соусов или специй', 95, now(), now()),
       (7, 'Нет приборов', 'Нет приборов', 94, now(), now()),
       (8, 'Отравление или аллергия', 'Отравление или аллергия', 93, now(), now()),
       (9, 'Инородный предмет в еде', 'Инородный предмет в еде', 92, now(), now()),
       (10, 'Блюдо не соответствует описанию', 'Блюдо не соответствует описанию', 91, now(), now()),
       (11, 'Неверный заказ', 'Неверный заказ', 90, now(), now()),
       (12, 'Клиент не удовлетворен доставкой (курьером)', 'Клиент не удовлетворен доставкой (курьером)', 89, now(), now()),
       (13, 'Угроза здоровью и жизни клиента со стороны курьера', 'Угроза здоровью и жизни клиента со стороны курьера', 89, now(), now()),
       (14, 'Заказ не доставлен', 'Заказ не доставлен', 89, now(), now()),
       (15, 'Проблема с рестораном', 'Проблема с рестораном', 88, now(), now()),
       (16, 'Долгое ожидание заказа в ресторане', 'Долгое ожидание заказа в ресторане', 100, now(), now()),
       (17, 'Проблема с приборами', 'Проблема с приборами', 94, now(), now()),
       (18, 'Автоматические при отмене заказа', 'Применяются при отмене заказов автоматически', 0, now(), now()),
       (19, 'Акции', 'Возникшие проблемы связанные с акциями', 0, now(), now()),
       (20, 'Другая проблема', 'Если клиенту не дали сдачу; если ситуация стандартная, но клиент сильно ругается', 0, now(), now()),
       (21, 'Проблема с чаевыми', 'Проблема с чаевыми', 0, now(), now());

SELECT setval('eats_compensations_matrix.situation_groups_id_seq', 21);


ALTER SEQUENCE eats_compensations_matrix.situations_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.situations (id, matrix_id, group_id, code, title, violation_level, responsible,
                                                  need_confirmation, priority, is_system, order_type, order_delivery_type, created_at, updated_at)
VALUES (1, 1, 1, 'small_delay', '<= 15 мин', 'low', 'company', false, 100, false, 3, 3, now(), now()),
       (2, 1, 1, 'medium_delay', 'Более 15 мин', 'low', 'company', false, 99, false, 3, 3, now(), now()),
       (3, 1, 1, 'long_delay', 'более 30 минут', 'low', 'company', false, 98, false, 3, 7, now(), now()),
       (4, 1, 2, 'raw_food', 'Сырая', 'low', 'place', true, 100, false, 3, 7, now(), now()),
       (5, 1, 2, 'fried_food', 'Пережаренная', 'low', 'place', true, 99, false, 3, 7, now(), now()),
       (6, 1, 2, 'expired_food', 'С истекшим сроком годности', 'medium', 'place', true, 98, false, 3, 7, now(), now()),
       (7, 1, 3, 'food_temperature_problem', 'Температура', 'low', 'place_or_courier', false, 100, false, 3, 7, now(), now()),
       (8, 1, 3, 'portion_size', 'Размер порции', 'low', 'place', true, 99, false, 3, 7, now(), now()),
       (9, 1, 3, 'taste_of_food_problems', 'Вкус', 'low', 'place', false, 98, false, 3, 7, now(), now()),
       (10, 1, 4, 'client_comment_ignored_without_allergic_reaction', 'Без аллергической реакции', 'low', 'place', false, 100, false, 3, 7, now(), now()),
       (11, 1, 4, 'client_comment_ignored_with_allergic_reaction', 'Возникла аллергия', 'medium', 'place', false, 100, false, 3, 7, now(), now()),
       (12, 1, 5, 'order_damaged_menu_item', 'Целое блюдо', 'low', 'place_or_courier', true, 100, false, 3, 7, now(), now()),
       (13, 1, 5, 'order_damaged_modifier', 'Гарнир, напиток или десерт', 'low', 'place_or_courier', true, 99, false, 3, 7, now(), now()),
       (14, 1, 6, 'no_sauces_requiring_payment', 'Платный соус или добавка', 'low', 'place', false, 100, false, 3, 7, now(), now()),
       (15, 1, 6, 'no_sauces_free', 'Соус или добавка в составе блюда (бесплатный)', 'low', 'place', false, 99, false, 3, 7, now(), now()),
       (16, 1, 7, 'no_cutlery_with_persons_count', 'Было указано количество', 'low', 'place', false, 100, false, 3, 3, now(), now()),
       (17, 1, 7, 'no_cutlery_without_persons_count', 'Не было указано количество', 'low', 'place', false, 99, false, 3, 3, now(), now()),
       (18, 1, 8, 'mild_poisoning', 'Незначительное ухудшение состояния здоровья', 'medium', 'place', false, 100, false, 3, 7, now(), now()),
       (19, 1, 8, 'severe_poisoning', 'Госпитализация, временная нетрудоспособность', 'high', 'place', false, 99, false, 3, 7, now(), now()),
       (20, 1, 9, 'foreign_object_in_food_can_not_injure', 'Не может потенциально поранить человека или привести к госпитализации', 'medium', 'place', true, 100, false, 3, 7, now(), now()),
       (21, 1, 9, 'foreign_object_in_food_can_injure', 'Может потенциально поранить человека или привести к госпитализации', 'high', 'place', true, 99, false, 3, 7, now(), now()),
       (22, 1, 10, 'description_mismatch_no_key_ingredient', 'Нет ключевого ингредиента', 'low', 'place', true, 100, false, 3, 7, now(), now()),
       (23, 1, 10, 'description_mismatch_no_additional_ingredient', 'Нет дополнительного ингредиента', 'low', 'place', false, 99, false, 3, 7, now(), now()),
       (24, 1, 11, 'wrong_menu_item', 'Неверное блюдо(а) или не хватает блюд(а)', 'low', 'place_or_courier', true, 100, false, 3, 7, now(), now()),
       (25, 1, 11, 'wrong_order', 'Заказ полностью неверный', 'low', 'place_or_courier', true, 100, false, 3, 7, now(), now()),
       (26, 1, 12, 'courier_problems', 'Клиент не удовлетворен доставкой', 'low', 'courier', false, 100, false, 3, 3, now(), now()),
       (27, 1, 13, 'threats_from_courier', 'Угроза здоровью и жизни клиента со стороны курьера', 'high', 'courier', false, 100, false, 3, 3, now(), now()),
       (28, 1, 14, 'not_confirmed_by_place', 'Не подтвержден рестораном', 'low', 'place', false, 100, false, 3, 3, now(), now()),
       (29, 1, 14, 'not_delivered_by_courier', 'Не доставлен курьером', 'low', 'courier', false, 99, false, 15, 7, now(), now()),
       (30, 1, 15, 'place_luring_customers', 'Переманивание клиентов в свой сервис', 'medium', 'place', false, 100, false, 3, 3, now(), now()),
       (31, 1, 15, 'threats_from_place_with_client', 'Оскорбление, угрозы в общении с клиентом', 'high', 'place', false, 99, false, 3, 3, now(), now()),
       (32, 1, 15, 'threats_from_place_with_courier', 'Оскорбление, угрозы в общении с курьером Я.Еды, поддержкой', 'medium', 'place', false, 99, false, 3, 3, now(), now()),
       (33, 1, 5, 'order_damaged_whole_order', 'Весь заказ', 'low', 'place_or_courier', true, 100, false, 3, 7, now(), now()),
       (34, 1, 16, 'small_delay_inside_place', '<= 15 мин', 'low', 'company', false, 100, false, 1, 4, now(), now()),
       (35, 1, 16, 'medium_delay_inside_place', 'Более 15 мин', 'low', 'company', false, 100, false, 1, 4, now(), now()),
       (36, 1, 17, 'no_cutlery', 'Нет приборов', 'low', 'company', false, 100, false, 1, 4, now(), now()),
       (37, 1, 17, 'extra_cutlery', 'Лишние приборы', 'low', 'company', false, 99, false, 1, 4, now(), now()),
       (38, 1, 15, 'order_was_not_transferred', 'Заказ не был передан', 'high', 'place', false, 99, false, 1, 4, now(), now()),
       (39, 1, 15, 'prepared_order_earlier', 'Приготовил заказ раньше', 'low', 'company', false, 100, false, 1, 4, now(), now()),
       (40, 1, 15, 'threats_in_communication_with_place', 'Оскорбление, угрозы в общении с рестораном', 'high', 'place', false, 98, false, 1, 4, now(), now()),
       (41, 1, 11, 'wrong_item', 'Неверный товар', 'low', 'place_or_courier', true, 100, false, 12, 7, now(), now()),
       (42, 1, 11, 'whole_order_is_incorrect', 'Заказ полностью неверный', 'low', 'place_or_courier', true, 99, false, 12, 7, now(), now()),
       (43, 1, 5, 'damaged_item', 'Товар', 'low', 'place_or_courier', true, 100, false, 12, 7, now(), now()),
       (44, 1, 5, 'damaged_order', 'Весь заказ', 'low', 'place_or_courier', true, 99, false, 12, 7, now(), now()),
       (45, 1, 16, 'long_delay_inside_place', 'Более 30 мин', 'low', 'company', false, 100, false, 1, 4, now(), now()),
       (46, 1, 18, 'order_cancel.place', 'Проблема с рестораном', 'low', 'place', false, 0, true, 3, 7, now(), now()),
       (47, 1, 18, 'order_cancel.courier', 'Проблема с курьером', 'low', 'courier', false, 0, true, 3, 7, now(), now()),
       (48, 1, 18, 'order_cancel.service', 'Проблема с сервисом', 'low', 'company', false, 0, true, 3, 7, now(), now()),
       (49, 1, 19, 'promo.one_plus_one', 'Недовоз по акции "1+1"', 'low', 'place', false, 0, false, 3, 3, now(), now()),
       (50, 1, 19, 'promo.gift', 'Недовоз подарка', 'low', 'place', false, 0, false, 3, 3, now(), now()),
       (51, 1, 20, 'other_problem.voucher', 'Купон', 'low', 'fate', false, 0, false, 31, 7, now(), now()),
       (52, 1, 20, 'other_problem.promocode', 'Промокод', 'low', 'fate', false, 0, false, 3, 7, now(), now()),
       (53, 1, 20, 'other_problem.refund', 'Возврат', 'low', 'fate', false, 0, false, 31, 7, now(), now()),
       (54, 1, 21, 'tips.refund_requested', 'Клиент запросил возврат', 'low', 'fate', false, 0, false, 3, 3, now(), now()),
       (55, 1, 18, 'order_cancel.place.pickup', 'Проблема с рестораном(самовывоз)', 'low', 'place', false, 0, true, 31, 7, now(), now());

SELECT setval('eats_compensations_matrix.situations_id_seq', 55);


ALTER SEQUENCE eats_compensations_matrix.compensation_packs_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.compensation_packs
(id, situation_id, available_source, max_cost, min_cost, compensations_count, payment_method_type, antifraud_score, country, created_at, updated_at)
VALUES (1, 2, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (2, 4, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (3, 4, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (4, 4, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (5, 4, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (6, 4, 1, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (7, 5, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (8, 5, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (9, 5, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (10, 5, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (11, 5, 1, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (12, 6, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (13, 6, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (14, 6, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (15, 6, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (16, 6, 1, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (17, 7, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (18, 10, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (19, 10, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (20, 10, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (21, 10, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (22, 10, 1, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (23, 11, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (24, 11, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (25, 11, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (26, 11, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (27, 11, 1, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (28, 12, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (29, 12, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (30, 12, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (31, 12, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (32, 12, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (33, 12, 1, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (34, 33, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (35, 33, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (36, 33, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (37, 33, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (38, 33, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (39, 33, 1, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (40, 13, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (41, 13, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (42, 13, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (43, 13, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (44, 13, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (45, 13, 1, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (46, 14, 7, null, null, 0, 'card', 'all', 'all', now(), now()),
       (47, 14, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (48, 16, 7, null, null, 0, 'all', 'all', 'all', now(), now()),
       (49, 18, 7, null, null, 0, 'card', 'all', 'all', now(), now()),
       (50, 18, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (51, 19, 7, null, null, 0, 'card', 'all', 'all', now(), now()),
       (52, 19, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (53, 20, 7, null, null, 0, 'card', 'all', 'all', now(), now()),
       (54, 20, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (55, 21, 7, null, null, 0, 'card', 'all', 'all', now(), now()),
       (56, 21, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (57, 22, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (58, 22, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (59, 22, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (60, 22, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (61, 22, 1, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (62, 24, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (63, 24, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (64, 24, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (65, 24, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (66, 24, 1, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (67, 25, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (68, 25, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (69, 25, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (70, 25, 6, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (71, 25, 1, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (72, 27, 7, null, null, 0, 'card', 'all', 'all', now(), now()),
       (73, 27, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (74, 28, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (75, 29, 7, 1499, null, 0, 'card', 'all', 'all', now(), now()),
       (76, 29, 7, null, 1500, 0, 'card', 'all', 'all', now(), now()),
       (77, 29, 7, 1499, null, 0, 'cash', 'all', 'all', now(), now()),
       (78, 29, 7, null, 1500, 0, 'cash', 'all', 'all', now(), now()),
       (79, 31, 7, null, null, 0, 'card', 'all', 'all', now(), now()),
       (80, 31, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (81, 10, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (82, 11, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (83, 33, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (84, 13, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (85, 18, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (86, 19, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (87, 20, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (88, 21, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (89, 22, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (90, 24, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (91, 25, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (92, 27, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (93, 31, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (94, 12, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (95, 14, 15, null, null, 1, 'all', 'all', 'all', now(), now()),
       (96, 35, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (97, 38, 15, null, null, 0, 'card', 'all', 'all', now(), now()),
       (98, 39, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (99, 40, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (100, 43, 15, null, null, 1, 'all', 'all', 'all', now(), now()),
       (101, 43, 15, null, null, 1, 'card', 'all', 'all', now(), now()),
       (102, 44, 15, null, null, 1, 'card', 'all', 'all', now(), now()),
       (103, 41, 15, null, null, 1, 'all', 'all', 'all', now(), now()),
       (104, 41, 15, null, null, 1, 'card', 'all', 'all', now(), now()),
       (105, 42, 15, null, null, 1, 'all', 'all', 'all', now(), now()),
       (106, 42, 15, null, null, 1, 'card', 'all', 'all', now(), now()),
       (107, 29, 15, null, null, 1, 'all', 'all', 'all', now(), now()),
       (108, 29, 15, null, null, 1, 'card', 'all', 'all', now(), now()),
       (109, 44, 15, null, null, 1, 'all', 'all', 'all', now(), now()),
       (110, 46, 8, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (111, 46, 8, null, null, 0, 'card', 'all', 'all', now(), now()),
       (112, 47, 8, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (113, 47, 8, null, null, 0, 'card', 'all', 'all', now(), now()),
       (114, 49, 7, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (115, 49, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (116, 49, 6, null, null, 0, 'card', 'all', 'all', now(), now()),
       (117, 49, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (118, 50, 7, null, null, 0, 'all', 'all', 'all', now(), now()),
       (119, 51, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (120, 52, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (121, 52, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (122, 52, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (123, 52, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (124, 52, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (125, 53, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (126, 48, 8, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (127, 48, 8, null, null, 0, 'card', 'all', 'all', now(), now()),
       (128, 54, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (129, 4, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (130, 5, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (131, 6, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (132, 10, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (133, 11, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (134, 11, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (135, 12, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (136, 33, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (137, 13, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (138, 14, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (139, 18, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (140, 19, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (141, 20, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (142, 21, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (143, 22, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (144, 24, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (145, 25, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (146, 27, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (147, 29, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (148, 46, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (149, 49, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
       (150, 55, 8, null, null, 0, 'card', 'all', 'all', now(), now()),
       (151, 55, 8, null, null, 0, 'cash', 'all', 'all', now(), now()),
       (152, 3, 15, null, null, 0, 'all', 'all', 'all', now(), now()),
       (153, 45, 15, null, null, 0, 'all', 'all', 'all', now(), now());
SELECT setval('eats_compensations_matrix.compensation_packs_id_seq', 153);


ALTER SEQUENCE eats_compensations_matrix.compensation_packs_to_types_id_seq RESTART WITH 1;

INSERT INTO eats_compensations_matrix.compensation_packs_to_types
(id, pack_id, type_id)
VALUES (1, 1, 5), (2, 2, 14), (3, 3, 10), (4, 4, 10), (5, 5, 14),
       (6, 6, 14), (7, 7, 14), (8, 8, 10), (9, 9, 10), (10, 10, 14),
       (11, 11, 14), (12, 12, 14), (13, 13, 10), (14, 14, 10), (15, 15, 14),
       (16, 16, 14), (17, 17, 5), (18, 18, 14), (19, 18, 5), (20, 19, 10),
       (21, 19, 5), (22, 20, 10), (23, 20, 5), (24, 21, 14), (25, 21, 5),
       (26, 22, 14), (27, 22, 5), (28, 23, 14), (29, 23, 5), (30, 24, 10),
       (31, 24, 5), (32, 25, 10), (33, 25, 5), (34, 26, 14), (35, 26, 5),
       (36, 27, 14), (37, 27, 5), (38, 28, 10), (39, 28, 5), (40, 29, 14),
       (41, 29, 5), (42, 30, 10), (43, 30, 5), (44, 31, 14), (45, 31, 5),
       (46, 32, 14), (47, 32, 5), (48, 33, 14), (49, 33, 5), (50, 34, 11),
       (51, 34, 5), (52, 35, 15), (53, 35, 5), (54, 36, 11), (55, 36, 5),
       (56, 37, 15), (57, 37, 5), (58, 38, 15), (59, 38, 5), (60, 39, 15),
       (61, 39, 5), (62, 40, 10), (63, 40, 5), (64, 41, 14), (65, 41, 5),
       (66, 42, 10), (67, 42, 5), (68, 43, 14), (69, 43, 5), (70, 44, 14),
       (71, 44, 5), (72, 45, 14), (73, 45, 5), (74, 46, 10), (75, 47, 14),
       (76, 48, 5), (77, 49, 11), (78, 49, 5), (79, 50, 15), (80, 50, 5),
       (81, 51, 11), (82, 51, 9), (83, 52, 15), (84, 52, 9), (85, 53, 11),
       (86, 53, 6), (87, 54, 15), (88, 54, 6), (89, 55, 11), (90, 55, 7),
       (91, 56, 15), (92, 56, 7), (93, 57, 14), (94, 57, 5), (95, 58, 10),
       (96, 58, 5), (97, 59, 10), (98, 59, 5), (99, 60, 14), (100, 60, 5),
       (101, 61, 14), (102, 61, 5), (103, 62, 14), (104, 62, 5), (105, 63, 10),
       (106, 63, 5), (107, 64, 10), (108, 64, 5), (109, 65, 14), (110, 65, 5),
       (111, 66, 14), (112, 66, 5), (113, 67, 15), (114, 67, 5), (115, 68, 11),
       (116, 68, 5), (117, 69, 11), (118, 69, 5), (119, 70, 15), (120, 70, 5),
       (121, 71, 15), (122, 71, 5), (123, 72, 11), (124, 72, 9), (125, 73, 15),
       (126, 73, 9), (127, 74, 6), (128, 75, 11), (129, 75, 6), (130, 76, 11),
       (131, 76, 6), (132, 77, 6), (133, 78, 6), (134, 79, 11), (135, 79, 9),
       (136, 80, 15), (137, 80, 9), (138, 81, 5), (139, 82, 5), (140, 83, 5),
       (141, 84, 5), (142, 85, 5), (143, 86, 9), (144, 87, 6), (145, 88, 7),
       (146, 89, 5), (147, 90, 5), (148, 91, 5), (149, 92, 9), (150, 93, 9),
       (151, 94, 5), (152, 95, 14), (153, 96, 5), (154, 97, 10), (155, 98, 5),
       (156, 99, 9), (157, 100, 14), (158, 101, 10), (159, 102, 11), (160, 103, 14),
       (161, 104, 10), (162, 105, 15), (163, 106, 11), (164, 107, 15), (165, 108, 11),
       (166, 109, 15), (167, 110, 4), (168, 111, 3), (169, 112, 2), (170, 113, 1),
       (171, 114, 14), (172, 114, 5), (173, 115, 14), (174, 115, 5), (175, 116, 10),
       (176, 116, 5), (177, 117, 10), (178, 117, 5), (179, 118, 5), (180, 119, 12),
       (181, 120, 5), (182, 121, 6), (183, 122, 7), (184, 123, 8), (185, 124, 9),
       (186, 125, 10), (187, 126, 5), (188, 127, 5), (189, 128, 13), (190, 129, 14),
       (191, 130, 14), (192, 131, 14), (193, 132, 14), (194, 132, 5), (195, 133, 14),
       (196, 133, 5), (197, 134, 14), (198, 134, 5), (199, 135, 14), (200, 135, 5),
       (201, 136, 14), (202, 136, 5), (203, 137, 14), (204, 137, 5), (205, 138, 14),
       (206, 139, 14), (207, 139, 5), (208, 140, 14), (209, 140, 9), (210, 141, 14),
       (211, 141, 6), (212, 142, 14), (213, 142, 7), (214, 143, 14), (215, 143, 5),
       (216, 144, 14), (217, 144, 5), (218, 145, 14), (219, 145, 5), (220, 146, 14),
       (221, 146, 9), (222, 147, 14), (223, 147, 6), (224, 148, 14), (225, 148, 5),
       (226, 149, 14), (227, 149, 5), (228, 150, 5), (229, 151, 5), (230, 152, 6),
       (231, 153, 6);

SELECT setval('eats_compensations_matrix.compensation_packs_to_types_id_seq', 231);


UPDATE eats_compensations_matrix.situations SET order_type = 12, order_delivery_type=12 WHERE id = 29;
UPDATE eats_compensations_matrix.situations SET order_type = 1, order_delivery_type=1 WHERE id = 3;

INSERT INTO eats_compensations_matrix.compensation_packs
(id, situation_id, available_source, max_cost, min_cost, compensations_count, payment_method_type, antifraud_score, country, created_at, updated_at)
VALUES
(154, 29, 15, null, null, 1, 'all', 'all', 'all', now(), now()),
(155, 29, 15, null, null, 1, 'card', 'all', 'all', now(), now());

INSERT INTO eats_compensations_matrix.compensation_packs_to_types
(id, pack_id, type_id)
VALUES
(232, 154, 15),
(233, 155, 11);

INSERT INTO eats_compensations_matrix.situations (id, matrix_id, group_id, code, title, violation_level, responsible,
                                                  need_confirmation, priority, is_system, order_type, order_delivery_type, created_at, updated_at)
VALUES
(56, 1, 14, 'not_delivered_by_courier', 'Не доставлен курьером', 'low', 'courier', false, 99, false, 3, 3, now(), now()),
(57, 1, 1, 'long_delay', 'более 30 минут', 'low', 'company', false, 98, false, 3, 3, now(), now());

INSERT INTO eats_compensations_matrix.compensation_packs
(id, situation_id, available_source, max_cost, min_cost, compensations_count, payment_method_type, antifraud_score, country, created_at, updated_at)
VALUES
(156, 56, 7, 1499, null, 0, 'card', 'all', 'all', now(), now()),
(157, 56, 7, null, 1500, 0, 'card', 'all', 'all', now(), now()),
(158, 56, 7, 1499, null, 0, 'cash', 'all', 'all', now(), now()),
(159, 56, 7, null, 1500, 0, 'cash', 'all', 'all', now(), now()),
(160, 56, 15, null, null, 1, 'all', 'all', 'all', now(), now()),
(161, 56, 15, null, null, 1, 'card', 'all', 'all', now(), now()),
(162, 56, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
(163, 57, 15, null, null, 0, 'all', 'all', 'all', now(), now());

INSERT INTO eats_compensations_matrix.compensation_packs_to_types
(id, pack_id, type_id)
VALUES
(234, 156, 11),
(235, 156, 6),
(236, 157, 11),
(237, 157, 6),
(238, 158, 6),
(239, 159, 6),
(240, 160, 15),
(241, 161, 11),
(242, 162, 14),
(243, 162, 6),
(244, 163, 6);

INSERT INTO eats_compensations_matrix.compensation_packs
(id, situation_id, available_source, max_cost, min_cost, compensations_count, payment_method_type, antifraud_score, country, created_at, updated_at)
VALUES
(164, 56, 1, null, null, 0, 'card', 'all', 'all', now(), now()),
(165, 57, 15, null, null, 0, 'all', 'all', 'all', now(), now());

INSERT INTO eats_compensations_matrix.compensation_packs_to_types
(id, pack_id, type_id)
VALUES
(245, 164, 14),
(246, 164, 6),
(247, 165, 6);

SELECT setval('eats_compensations_matrix.situations_id_seq', 57);
SELECT setval('eats_compensations_matrix.compensation_packs_id_seq', 165);
SELECT setval('eats_compensations_matrix.compensation_packs_to_types_id_seq', 247);

DELETE from eats_compensations_matrix.compensation_packs_to_types where pack_id IN (110, 111, 112, 113, 126, 127, 148, 150, 151);
DELETE from eats_compensations_matrix.compensation_packs where id IN (110, 111, 112, 113, 126, 127, 148, 150, 151);
DELETE from eats_compensations_matrix.situations where id IN (46, 47, 48, 55);

COMMIT;
