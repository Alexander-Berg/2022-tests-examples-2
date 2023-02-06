INSERT INTO eats_picker_orders.orders (id, eats_id, last_version, picker_id, created_at, updated_at)
VALUES
    (1, 'eats_id_0', 0, 'picker_id_0', '2021-07-01T11:30:01.2345+03:00'::timestamptz, '2021-07-04T11:30:01.2345+03:00'::timestamptz),
    (2, 'eats_id_1', 0, 'picker_id_0', '2021-07-01T11:30:01.2345+03:00'::timestamptz, '2021-07-05T11:30:01.2345+03:00'::timestamptz),
    (3, 'eats_id_2', 0, 'picker_id_0', '2021-07-01T11:30:01.2345+03:00'::timestamptz, '2021-07-08T11:30:01.2345+03:00'::timestamptz),
    (4, 'eats_id_3', 0, 'picker_id_1', '2021-07-01T11:30:01.2345+03:00'::timestamptz, '2021-07-08T11:30:01.2345+03:00'::timestamptz),
    (5, 'eats_id_4', 0, 'picker_id_1', '2021-07-01T11:30:01.2345+03:00'::timestamptz, '2021-07-08T11:30:01.2345+03:00'::timestamptz);

INSERT INTO eats_picker_orders.order_statuses (id, order_id, last_version, state, created_at)
VALUES
    (1, 1, 0, 'new', '2021-07-02T11:30:01.2345+03:00'::timestamptz),
    (2, 1, 0, 'cancelled', '2021-07-04T11:30:01.2345+03:00'::timestamptz),
    (3, 2, 0, 'new', '2021-07-02T11:30:01.2345+03:00'::timestamptz),
    (4, 2, 0, 'waiting_dispatch', '2021-07-03T11:30:01.2345+03:00'::timestamptz),
    (5, 2, 0, 'dispatching', '2021-07-04T11:30:01.2345+03:00'::timestamptz),
    (6, 2, 0, 'assigned', '2021-07-05T11:30:01.2345+03:00'::timestamptz),
    (7, 3, 0, 'new', '2021-07-07T11:30:01.2345+03:00'::timestamptz),
    (8, 3, 0, 'complete', '2021-07-08T11:30:01.2345+03:00'::timestamptz);

INSERT INTO eats_picker_orders.order_talks (id, order_id, talk_id, length, status, created_at)
VALUES
    (1, 1, 'talk_id_0', 42, 'status_0', '2021-07-04T11:30:01.2345+03:00'::timestamptz),
    (2, 1, 'talk_id_1', 666, 'status_1', '2021-07-04T11:30:01.23456+03:00'::timestamptz),
    (3, 3, 'talk_id_2', 777, 'status_2', '2021-07-08T11:30:01.23456+03:00'::timestamptz),
    (4, 5, 'talk_id_3', 777, 'status_2', '2021-07-08T11:30:01.23456+03:00'::timestamptz);
