
/* V1 */
INSERT INTO orders.orders
(order_id, arrive_time, link_id, last_proceed_time, is_processing_change_time, is_processing)
VALUES ('delayed_order_id_1',
        TIMESTAMP '2019-02-03T04:00:00',
        'link_1',
        TIMESTAMP '2019-02-03T00:00:00',
        TIMESTAMP '2019-02-03T00:00:00', FALSE),
       ('delayed_order_id_2',
        TIMESTAMP '2019-02-03T04:00:00',
        'link_2',
        TIMESTAMP '2019-02-03T00:00:00',
        TIMESTAMP '2019-02-03T03:45:00', TRUE);
