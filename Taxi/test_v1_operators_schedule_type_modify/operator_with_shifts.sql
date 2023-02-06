insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;

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
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        '2023-08-01 00:00:00.0',
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
        'uid3',
        1.0,
        '2020-08-26 00:00:00.0',
        null
    );

INSERT INTO callcenter_operators.skills
    (
        name,
        description,
        active
    )
VALUES
    (
        'hokage',
        '',
        True
    ),
    (
        'sixth_hokage',
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
        'uid3',
        1,
        '2023-08-01 00:00:00.0+00',
        NULL,
        '2020-06-26 00:00:00.0'
    );

INSERT INTO callcenter_operators.operators_schedule_type_skills
    (
        operators_schedule_types_id,
        skill
    )
VALUES
    (
        1,
        'hokage'
    );

INSERT INTO callcenter_operators.operators_shifts
    (
        yandex_uid,
        skill,
        start,
        duration_minutes,
        frozen,
        type,
        description,
        operators_schedule_types_id
    )
VALUES
    (
        'uid3',
        'hokage',
        '2023-08-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1
    ),
    (
        'uid3',
        'hokage',
        '2023-09-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1
    ),
    (
        'uid3',
        'hokage',
        '2023-09-27 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1
    );
