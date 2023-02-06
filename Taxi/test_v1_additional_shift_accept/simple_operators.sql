
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
    );

INSERT INTO callcenter_operators.skills
    (
        name,
        description,
        active
    )
VALUES
    (
        'tatarin',
        '',
        True
    ),
    (
        'hokage',
        '',
        True
    );

INSERT INTO callcenter_operators.operators_schedule_types
    (
        yandex_uid,
        unique_operator_id,
        schedule_type_id,
        starts_at,
        expires_at,
        updated_at
    )
VALUES
    (
        'uid1',
        1,
        1,
        '2020-07-01 00:00:00.0+00',
        '2020-08-01 00:00:00.0+00',
        '2020-06-26 00:00:00.0'
    ),
    (
        'uid2',
        2,
        2,
        '2020-07-25 00:00:00.0+00',
        NULL,
        '2020-06-26 00:00:00.0'
    );


INSERT INTO callcenter_operators.operators_schedule_type_skills
    (
        skill,
        operators_schedule_types_id,
        updated_at
    )
VALUES
    (
        'hokage',
        1,
        '2020-06-26 00:00:00.0'
    ),
    (
        'tatarin',
        2,
        '2020-06-26 00:00:00.0'
    );
