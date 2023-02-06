INSERT INTO eats_compensations_matrix.order_cancel_matrices (version_code,
                                                             parent_version_code,
                                                             approved_at,
                                                             author,
                                                             approve_author,
                                                             created_at,
                                                             updated_at)
VALUES ('cancel_v.1.0',
        NULL,
        NULL,
        'nevladov',
        NULL,
        '2020-06-23T08:00:00+00:00',
        '2020-06-23T08:00:00+00:00'),
       ('cancel_v.2.0',
        NULL,
        '2020-06-23T09:00:00+00:00',
        'nevladov',
        'nevladov_test',
        '2020-06-23T08:00:00+00:00',
        '2020-06-23T08:00:00+00:00'),
       ('cancel_v.3.0',
        NULL,
        NULL,
        'nevladov',
        NULL,
        '2020-06-23T08:00:00+00:00',
        '2020-06-23T08:00:00+00:00');

INSERT INTO eats_compensations_matrix.order_cancel_reason_groups (name,
                                                                  code,
                                                                  created_at,
                                                                  updated_at)
VALUES ('Ресторан', 'place', '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00'),
       ('Клиент', 'client', '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00'),
       ('Курьер', 'courier', '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00');


INSERT INTO eats_compensations_matrix.order_cancel_reasons (matrix_id,
                                                            group_id,
                                                            name,
                                                            code,
                                                            priority,
                                                            type,
                                                            order_type,
                                                            order_delivery_type,
                                                            created_at,
                                                            updated_at,
                                                            deleted_at,
                                                            payment_type,
                                                            allowed_callers,
                                                            allowed_countries)
VALUES (1, 1, 'Невозможно дозвониться до ресторана', 'place.unable_to_call', 105, 'unknown', 28, 0,
        '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00', null, 1, 1, array ['ru']),
       (1, 2, 'Отсутствует блюдо', 'place.missing_dish', 101, 'unknown', 28, 0, '2020-06-23T08:00:00+00:00',
        '2020-06-23T08:00:00+00:00', null, 2, 1, array ['kz']),
       (2, 2, 'Закрылся раньше', 'place.closed_early', 104, 'unknown', 3, 3, '2020-06-23T08:00:00+00:00',
        '2020-06-23T08:00:00+00:00', null, 3, 1, array ['by']),
       (1, 2, 'Закрылся раньше', 'place.closed_early', 101, 'unknown', 28, 0, '2020-06-23T08:00:00+00:00',
        '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00', 2, 1, array ['kz']),
       (3, 2, 'Закрылся раньше', 'place.closed_early', 101, 'unknown', 28, 0, '2020-06-23T08:00:00+00:00',
        '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00', 2, 1, array ['kz']),
       (3, 2, 'Закрылся намного раньше', 'place.closed_early', 101, 'unknown', 28, 0, '2020-06-23T08:00:00+00:00',
        '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00', 2, 1, array ['kz']);


INSERT INTO eats_compensations_matrix.order_cancel_reactions
    (type, payload, created_at, updated_at, deleted_at)
VALUES ('order.cancel.reaction.compensation', '{"limit":100,"limit_currency":"RUB","rate":15}', '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00', null),
       ('order.cancel.reaction.compensation', '{"limit":200,"limit_currency":"BYN","rate":25}', '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00', null),
       ('order.cancel.reaction.return_promocode', '{}', '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00', null),
       ('order.cancel.reaction.return_promocode', '{}', '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00', null),
       ('order.cancel.reaction.return_promocode', '{}', '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00');

INSERT INTO eats_compensations_matrix.order_cancel_reasons_reactions
    (reason_id, reaction_id, minimal_cost, minimal_eater_reliability, is_allowed_before_place_confirmed,
     is_allowed_for_fast_cancellation, is_for_vip_only, deleted_at)
VALUES
       (1, 1, 100, 'good', true, true, true, NULL),
       (1, 3, 100, 'bad', true, true, true, NULL),
       (1, 5, 100, 'good', true, true, true, NULL),
       (2, 3, 100, 'bad', true, true, true, NULL),
       (3, 4, 100, 'good', true, true, true, NULL),
       (2, 2, 100, 'bad', true, true, true, '2020-06-23T08:00:00+00:00'),
       (2, 1, 100, 'good', true, true, true, NULL),
       (2, 1, 100, 'good', false, false, false, NULL);


INSERT INTO eats_compensations_matrix.compensation_types (id, type, rate, description, full_refund, max_value,
                                                          min_value, notification, created_at, updated_at)
VALUES (1, 'promocode', 10, null, false, null, null, 'order.compensation.cancel.courier.card',
        '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00'),
       (2, 'promocode', 10, null, false, null, null, 'order.compensation.cancel.courier.cash',
        '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00'),
       (3, 'promocode', 10, null, false, null, null, 'order.compensation.cancel.place.card',
        '2020-06-23T08:00:00+00:00', '2020-06-23T08:00:00+00:00'),
       (4, 'refund', 10, null, false, null, null, 'order.compensation.cancel.place.card', '2020-06-23T08:00:00+00:00',
        '2020-06-23T08:00:00+00:00');

INSERT INTO eats_compensations_matrix.order_cancel_matrices (version_code,
                                                             author,
                                                             deleted_at)

VALUES ('cancel_v.4.0',
        'Alice',
        '2021-01-01T08:00:00+00:00');

INSERT INTO eats_compensations_matrix.order_cancel_matrices (version_code,
                                                             parent_version_code,
                                                             approved_at,
                                                             author,
                                                             approve_author,
                                                             created_at,
                                                             updated_at)
VALUES ('cancel_v.5.0',
        NULL,
        '2020-06-23T09:00:00+00:00',
        'sumltship',
        'sumltship_test',
        '2020-06-23T08:00:00+00:00',
        '2020-06-23T08:00:00+00:00');
