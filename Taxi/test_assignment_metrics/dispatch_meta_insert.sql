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
    last_dispatch_run
    )
VALUES
    (
        1,
        'user_id_1',
        'offer_id_1',
        'good_order',
        NOW() - '1 minute'::interval,
        'example',
        'moscow',
        'taxi',
        'dispatched',
        '{"econom"}',
        NOW() - '1 minute'::interval,
        NOW()
    ),
    (
        2,
        'user_id_1',
        'offer_id_2',
        'too_old_order',
        NOW() - '5 minute'::interval,
        'example',
        'moscow',
        'taxi',
        'idle',
        '{"business"}',
        NOW() - '5 minute'::interval,
        NOW() - '3 minute'::interval
    ),
    (
        3,
        'user_id_1',
        'offer_id_3',
        'order_in_idle_state',
        NOW() - '1 minute'::interval,
        'example',
        'spb',
        'taxi',
        'idle',
        '{"comfortplus"}',
        NOW() - '1 minute'::interval,
        NOW()
);

INSERT INTO dispatch_buffer.order_meta (
    id, order_meta
) VALUES (1, '{}'::jsonb),
         (2, '{}'::jsonb),
         (3, '{}'::jsonb);
