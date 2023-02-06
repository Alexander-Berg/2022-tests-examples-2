insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;

insert into callcenter_operators.shift_events (id, alias, description)
VALUES (0, 'tutoring', 'tutor tutoring students')
on conflict do nothing;

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
        'uid2',
        1,
        '2020-07-01 00:00:00.0+00',
        '2020-08-01 00:00:00.0+00',
        '2020-06-26 00:00:00.0'
    );


INSERT INTO callcenter_operators.operators_shifts
    (
        yandex_uid,
        skill,
        start,
        duration_minutes,
        frozen,
        type,
        description
    )
VALUES
    (
        'uid1',
        'hokage',
        '2020-07-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    ),
        (
        'uid3',
        'pokemon',
        '2020-07-26 13:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    ),
        (
        'uid3',
        'pokemon',
        '2020-07-26 14:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    ),
    (
        'uid2',
        'pokemon',
        '2020-08-03 15:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    ),
        (
        'uid3',
        'pokemon',
        '2020-07-26 16:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    );
