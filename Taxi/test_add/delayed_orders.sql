
/* V1 */
INSERT INTO orders.orders
       (order_id, arrive_time, last_proceed_time, link_id,
        is_processing_change_time)
VALUES
       ('already_existing_order_id',
        TIMESTAMP '2019-02-04',
        TIMESTAMP '2019-02-03',
        'link_5',
        TIMESTAMP '2019-02-02');
