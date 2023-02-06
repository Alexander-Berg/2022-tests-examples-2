
INSERT INTO callcenter_operators.schedule_types
    (
        schedule_alias,
        schedule,
        first_weekend,
        start,
        duration_minutes,
        rotation_type,
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
        'sequentially',
        '2020-08-26 12:00:00.0',
        'taxi'
    ),
    (
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        'weekly',
        '2020-08-26 00:00:00.0',
        'taxi'
    ),
    (
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        'weekly',
        '2020-08-26 00:00:00.0',
        'taxi'
    ),
    (
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        'weekly',
        '2023-08-01 00:00:00.0',
        'taxi'
    ),
    (
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        'weekly',
        '2020-08-26 00:00:00.0',
        'lavka'
    );

INSERT INTO callcenter_operators.schedule_types
    (
        schedule_type_id,
        schedule_alias,
        schedule,
        first_weekend,
        start,
        duration_minutes,
        rotation_type,
        updated_at,
        domain
    )
VALUES
    (
        9999,
        'abnormal-schedule-in-response',
        '{5, 2}',
        FALSE,
        '21:00',
        14 * 60,
        'weekly',
        '2023-08-01 00:00:00.0',
        'taxi'
    );


INSERT INTO callcenter_operators.unique_operators
    (
        id,
        yandex_uid,
        domain,
        employee_uid
    )
VALUES
    (
        1,
        'uid1',
        'taxi',
        '00000000-0000-0000-0000-000000000001'
    ),
    (
        2,
        'uid2',
        'taxi',
        '00000000-0000-0000-0000-000000000002'
    ),
    (
        3,
        'uid3',
        'taxi',
        '00000000-0000-0000-0000-000000000003'
    ),
    (
        7,
        'uid4',
        'taxi',
        '00000000-0000-0000-0000-000000000004'
    ),
    (
        5,
        'uid5',
        'taxi',
        '00000000-0000-0000-0000-000000000005'
    ),
    (
        9999,
        'uid-to-verify-schedules',
        'taxi',
        '00000000-9999-0000-0000-000000000000'
    );

INSERT INTO callcenter_operators.operators
    (
        yandex_uid,
        rate,
        updated_at,
        tags,
        unique_operator_id
    )
VALUES
    (
        'uid1',
        0.5,
        '2020-08-26 00:00:00.0',
        ARRAY['naruto'],
        1
    ),
    (
        'uid2',
        1.0,
        '2020-08-27 01:00:00.0',
        ARRAY['naruto', 'driver'],
        2
    ),
    (
        'uid3',
        1.0,
        '2020-08-26 00:00:00.0',
        null,
        3
    ),
    (
        'uid4',
        0.99,
        '2020-08-26 00:00:00.0',
        ARRAY['naruto'],
        7
    ),
    (
        'uid5',
        0.99,
        '2020-08-26 00:00:00.0',
        ARRAY['naruto'],
        5
    ),
    (
        'uid-to-verify-schedules',
        NULL,
        '2020-08-26 00:00:00.0',
        NULL,
        9999
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
        updated_at,
        unique_operator_id
    )
VALUES
    (
        'uid1',
        1,
        '2020-07-01 00:00:00.0+00',
        '2020-08-01 00:00:00.0+00',
        '2020-06-26 00:00:00.0',
        NULL
    ),
    (
        'uid2',
        2,
        '2020-08-01 00:00:00.0+00',
        NULL,
        '2020-06-26 00:00:00.0',
        NULL
    ),
    (
        'uid3',
        4,
        '2023-08-01 00:00:00.0+00',
        NULL,
        '2020-06-26 00:00:00.0',
        3
    ),
    (
        'uid-to-verify-schedules',
        9999,
        '2023-08-01 00:00:00.0+00',
        NULL,
        '2020-06-26 00:00:00.0',
        NULL
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
    ),
    (
        4,
        'hokage',
        TRUE,
        '2020-06-26 00:00:00.0'
    );
