INSERT INTO cargo_orders.orders_client_robocall_attempts (order_id, point_id, attempt_id, updated_ts)
VALUES ('11111111-1111-1111-1111-111111111111'::UUID,
        'point_1'::TEXT,
        1::INT,
        '2020-07-12T09:59:59+03:00'::TIMESTAMPTZ),
       ('22222222-2222-2222-2222-222222222222'::UUID,
        'point_2'::TEXT,
        2::INT,
        '2020-07-12T10:00:01+03:00'::TIMESTAMPTZ);
