insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}')
on conflict do nothing;

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
        NULL,
        '{2, 2}',
        FALSE,
        '12:00',
        8 * 60,
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
    );


INSERT INTO callcenter_operators.operators
    (
        yandex_uid,
        rate,
        updated_at
    )
VALUES
    (
        'uid1',
        0.5,
        '2020-08-26 00:00:00.0'
    ),
    (
        'uid2',
        1.0,
        '2020-08-27 01:00:00.0'
    ),
    (
        'uid3',
        1.0,
        '2020-08-27 01:00:00.0'
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
    );

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
        '2020-07-15 00:00:00.0+00',
        '2020-06-26 00:00:00.0'
    ),
    (
        'uid2',
        3,
        '2021-08-01 00:00:00.0+00',
        '2022-08-01 00:00:00.0+00',
        '2020-06-26 00:00:00.0'
    ),
    (
        'uid2',
        2,
        '2020-08-01 00:00:00.0+00',
        '2021-08-01 00:00:00.0+00',
        '2020-06-26 00:00:00.0'
    ),
    (
        'uid3',
        2,
        '2020-08-01 00:00:00.0+00',
        NULL,
        '2020-06-26 00:00:00.0'
    );
