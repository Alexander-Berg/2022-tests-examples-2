INSERT INTO callcenter_operators.operators_actual_events
(yandex_uid,
 meta_queues,
 start,
 type,
 sub_type
)
VALUES ('uid1',
        ARRAY['pokemon'],
        '2020-07-26 12:00:00.0 +0000',
        'connected',
        NULL
        ),
       ('uid1',
        ARRAY['pokemon'],
        '2020-07-26 14:00:00.0 +0000',
        'disconnected',
        NULL
        ),
       ('uid2',
        ARRAY['pokemon'],
        '2020-07-26 12:00:00.0 +0000',
        'connected',
        NULL
        ),
       ('uid2',
        ARRAY['pokemon'],
        '2020-07-26 13:00:00.0 +0000',
        'paused',
        'dinner'
        ),
       ('uid2',
        ARRAY['pokemon'],
        '2020-07-26 13:30:00.0 +0000',
        'connected',
        NULL
        ),
       ('uid2',
        ARRAY['pokemon'],
        '2020-07-26 15:00:00.0 +0000',
        'disconnected',
        NULL
        );
