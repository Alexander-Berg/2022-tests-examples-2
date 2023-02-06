
/* V1 */
INSERT INTO orders.orders
    (order_id, arrive_time, link_id, last_proceed_time)
VALUES ('delayed_order_id', TIMESTAMP '2019-02-02', 'link_1', TIMESTAMP '2019-02-03');

INSERT INTO orders.dispatched_orders
    (order_id, arrive_time, dispatch_time)
VALUES ('dispatched_order_id', TIMESTAMP '2019-02-04', TIMESTAMP '2019-02-05');
