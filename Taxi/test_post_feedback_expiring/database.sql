INSERT INTO eats_feedback.orders
    (order_nr, order_delivered_at, status, eater_id)
VALUES ('102', '2021-02-10T12:23:00+00:00', 'finished', '111'),
       ('103', '2021-02-11T12:23:00+00:00', 'finished', '111'),
       ('104', '2021-02-13T12:23:00+00:00', 'finished', '111'),
       ('105', '2021-02-13T12:23:00+00:00', 'finished', '112'),
       ('106', '2021-02-10T11:23:00+00:00', 'finished', '112'),
       ('107', '2021-02-13T11:23:00+00:00', 'finished', '112');

INSERT INTO eats_feedback.predefined_comments (id, tanker_key, code, version, type, group_code, generate_sorrycode,
                                               calculate_average_rating_place, access_mask_for_order_flow,
                                               show_position, rating_flow_types,
                                               created_at, deleted_at, flow_types, delivery_types)
VALUES (1, 'dislike.food', 'DISLIKE_FOOD', 'default', 'dislike', NULL, FALSE, TRUE, 1, 100,
        '{native, lavka, shop, pharmacy, bk_logist, retail}', '2017-12-15 15:49:46', NULL,
        '{native, lavka, pharmacy, bk_logist}', '{marketplace, our_delivery}');

INSERT INTO eats_feedback.predefined_comments (id, tanker_key, code, version, type, group_code, generate_sorrycode,
                                               calculate_average_rating_place, access_mask_for_order_flow,
                                               show_position, rating_flow_types,
                                               created_at, deleted_at, flow_types, delivery_types)
VALUES (3, 'dislike.incorrectly_assembled_order', 'WRONG_SET', 'default', 'dislike', NULL, FALSE, FALSE, 1, 200,
        '{native, lavka, shop, pharmacy, bk_logist}', '2017-12-15 15:49:46', NULL,
        '{native, lavka, pharmacy, bk_logist}', '{marketplace, our_delivery}');
