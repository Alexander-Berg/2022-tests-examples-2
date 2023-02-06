insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;

insert into callcenter_operators.shift_events (id, alias, description, updated_at)
VALUES (0, 'tutoring', 'tutor tutoring students', '2020-11-16 14:10:00.0')
on conflict do nothing;

INSERT INTO callcenter_operators.operators_shifts
    (
        id,
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
        0,
        'uid1',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        120,
        FALSE,
        1,
        'empty'
    ),
    (
        1,
        'uid2',
        'pokemon',
        '2020-08-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    );

INSERT INTO callcenter_operators.operators_breaks
    (
        shift_id,
        start,
        duration_minutes,
        type
    )
VALUES
    (
        0,
        '2020-07-26 12:00:00.0 +0000',
        30,
        'technical'
    ),
    (
        0,
        '2020-07-26 12:30:00.0 +0000',
        30,
        'technical'
    ),
    (
        0,
        '2020-07-26 13:00:00.0 +0000',
        30,
        'technical'
    ),
    (
        0,
        '2020-07-26 13:30:00.0 +0000',
        30,
        'technical'
    )
