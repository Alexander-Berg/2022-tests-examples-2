INSERT INTO eats_eta.orders (id, order_nr, status_changed_at)
VALUES
    (1, 'order_nr_1', '2021-07-01T11:00:00.0000+03:00'::timestamptz),
    (2, 'order_nr_2', '2021-07-01T12:00:00.0000+03:00'::timestamptz),
    (3, 'order_nr_3', '2021-07-01T12:00:00.0001+03:00'::timestamptz),
    (4, 'order_nr_4', '2021-07-02T12:00:00.0000+03:00'::timestamptz),
    (5, 'order_nr_5', '2021-07-03T12:00:00.0000+03:00'::timestamptz);
