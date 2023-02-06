
INSERT INTO callcenter_operators.schedule_types
    (
        schedule_alias,
        schedule,
        first_weekend,
        start,
        duration_minutes,
        updated_at,
        domain
    )
VALUES
    (
        NULL,
        '{2, 2}',
        FALSE,
        '12:00',
        12 * 60,
        '2020-08-26 12:00:00.0',
        'taxi'
    ),
    (
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        '2020-08-26 00:00:00.0',
        'taxi'
    ),
    (
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        '2020-08-26 00:00:00.0',
        'taxi'
    ),
    (
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        '2023-08-01 00:00:00.0',
        'taxi'
    );


INSERT INTO callcenter_operators.unique_operators
    (
        yandex_uid,
        domain,
        employee_uid
    )
VALUES
    (
        'uid1',
        'taxi',
        '00000000-0000-0000-0000-000000000001'
    ),
    (
        'uid2',
        'taxi',
        '00000000-0000-0000-0000-000000000002'
    ),
    (
        'uid3',
        'taxi',
        '00000000-0000-0000-0000-000000000003'
    ),
    (
        'uid4',
        'taxi',
        '00000000-0000-0000-0000-000000000004'
    ),
    (
        'uid5',
        'taxi',
        '00000000-0000-0000-0000-000000000005'
    ),
    (
        'not-existing',
        'taxi',
        'deadbeef-0000-0000-0000-000000000000'
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
    ),
    (
        'uid5',
        0.99,
        '2020-08-26 00:00:00.0',
        ARRAY['naruto']
    ),
    (
        'not-existing',
        NULL,
        '2020-08-26 00:00:00.0',
        NULL
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

INSERT INTO callcenter_operators.operators_schedule_types
    (
        yandex_uid,
        schedule_type_id,
        starts_at,
        expires_at,
        updated_at
    )
VALUES
    (
        'uid1',
        1,
        '2020-07-01 00:00:00.0+00',
        '2020-08-01 00:00:00.0+00',
        '2020-06-26 00:00:00.0'
    ),
    (
        'uid2',
        2,
        '2020-08-01 00:00:00.0+00',
        NULL,
        '2020-06-26 00:00:00.0'
    ),
    (
        'uid3',
        4,
        '2023-08-01 00:00:00.0+00',
        NULL,
        '2020-06-26 00:00:00.0'
    );


INSERT INTO callcenter_operators.operators_schedule_type_skills
    (
        operators_schedule_types_id,
        skill,
        is_primary,
        updated_at
    )
VALUES
    (
        1,
        'hokage',
        TRUE,
        '2020-06-26 00:00:00.0'
    ),
    (
        1,
        'tatarin',
        FALSE,
        '2020-06-26 00:00:00.0'
    ),
    (
        2,
        'tatarin',
        TRUE,
        '2020-06-26 00:00:00.0'
    ),
    (
        2,
        'pokemon',
        FALSE,
        '2020-06-26 00:00:00.0'
    ),
    (
        3,
        'hokage',
        TRUE,
        '2020-06-26 00:00:00.0'
    );
