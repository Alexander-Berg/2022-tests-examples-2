INSERT INTO callcenter_operators.schedule_types
    (
        schedule_alias,
        schedule,
        first_weekend,
        start,
        duration_minutes,
        rotation_type,
        updated_at,
        domain,
        properties,
        offset_settings
    )
VALUES
    (
        NULL,
        '{2, 2}',
        FALSE,
        '12:00',
        12 * 60,
        'sequentially',
        '2020-08-26 12:00:00.0',
        'taxi',
        '{"performance_standard": 480}',
        NULL
    ),
    (
        NULL,
        '{2, 2}',
        FALSE,
        '12:00',
        12 * 60,
        'sequentially',
        '2020-08-26 12:00:00.0',
        'taxi',
        '{"performance_standard": 420}',
        '[{"oebs_alias": "blabla", "offset_alias": "blablabla", "offset": 2}]'
    ),
    (
        NULL,
        NULL,
        FALSE,
        NULL,
        NULL,
        NULL,
        '2020-08-26 12:00:00.0',
        'taxi',
        '{"performance_standard": 420}',
        NULL
    );
