
INSERT INTO callcenter_operators.schedule_types
    (
        schedule_alias,
        schedule,
        first_weekend,
        start,
        duration_minutes,
        updated_at
    )
VALUES
    (
        'schedule_one',
        '{2, 2}',
        FALSE,
        '12:00',
        12 * 60,
        '2020-08-26 12:00:00.0'
    ),
    (
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        '2020-08-26 00:00:00.0'
    ),
    (
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        '2020-08-26 00:00:00.0'
    ),
    (
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        '2023-08-01 00:00:00.0'
    );


INSERT INTO callcenter_operators.operators
    (
        yandex_uid,
        rate,
        updated_at,
        tags
    )
VALUES
    (
        'uid1',
        0.5,
        '2020-08-26 00:00:00.0',
        ARRAY['naruto']
    ),
    (
        'uid2',
        1.0,
        '2020-08-27 01:00:00.0',
        ARRAY['naruto', 'driver']
    ),
    (
        'uid3',
        1.0,
        '2020-08-26 00:00:00.0',
        null
    ),
    (
        'uid4',
        0.99,
        '2020-08-26 00:00:00.0',
        ARRAY['naruto']
    );

INSERT INTO callcenter_operators.skills
    (
        name,
        description,
        active
    )
VALUES
    (
        'pokemon',
        '',
        True
    ),
    (
        'tatarin',
        '',
        True
    ),
    (
        'droid',
        '',
        True
    ),
    (
        'unknown',
        '',
        True
    ),
    (
        'order',
        '',
        True
    ),
    (
        'hokage',
        '',
        True
    ),
    (
        '21',
        '',
        True
    )
ON CONFLICT (name) DO NOTHING;
