INSERT INTO dispatch_buffer.dispatch_meta
    (
    id,
    user_id,
    offer_id,
    order_id,
    created,
    zone_id,
    agglomeration,
    service,
    dispatch_status,
    classes,
    first_dispatch_run,
    last_dispatch_run,
    order_lookup
    )
VALUES
    (
        1,
        'user_id_1',
        'offer_id_1',
        'order_id_1',
        NOW() - '3 minute'::interval,
        'example',
        'example_agglomeration',
        'taxi',
        'dispatched',
        '{"comfort"}',
        NOW() - '60 seconds'::interval,
        NOW(),
        ROW(0,1,3)
    ),
    (
        2,
        'user_id_1',
        'offer_id_2',
        'order_id_2',
        NOW() - '2 minute'::interval,
        'example',
        'example_agglomeration',
        'taxi',
        'dispatched',
        '{"business"}',
        NOW() - '60 seconds'::interval,
        NOW(),
        ROW(0,1,3)
    ),
    (
        3,
        'user_id_1',
        'offer_id_3',
        'order_id_3',
        NOW() - '2 minute'::interval,
        'example',
        'example_agglomeration',
        'taxi',
        'idle',
        '{"business"}',
        NOW() - '120 seconds'::interval,
        NOW(),
        ROW(0,1,3)
    ),
    (
        4,
        'user_id_1',
        'offer_id_4',
        'order_id_4',
        NOW() - '2 minute'::interval,
        'example',
        'example_agglomeration',
        'taxi',
        'idle',
        '{"business"}',
        NOW() - '120 seconds'::interval,
        NOW(),
        ROW(0,1,3)
    ),
    (
        5,
        'user_id_1',
        'offer_id_5',
        'order_id_5',
        NOW() - '3 minute'::interval,
        'example',
        'example_agglomeration',
        'taxi',
        'on_draw',
        '{"comfort"}',
        NOW() - '120 seconds'::interval,
        NOW(),
        ROW(0,1,3)
    );

INSERT INTO dispatch_buffer.order_meta (
    id, order_meta
) VALUES (1, '{}'::jsonb),
         (2, '{}'::jsonb),
         (3, '{}'::jsonb),
         (4, '{}'::jsonb),
         (5, '{}'::jsonb);
