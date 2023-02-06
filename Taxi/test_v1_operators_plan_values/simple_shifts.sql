insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;

insert into callcenter_operators.shift_events (id, alias, description)
VALUES (0, 'tutoring', 'tutor tutoring students')
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
        'order',
        '2020-08-26 13:00:00.0 +0000',
        180,
        FALSE,
        1,
        'empty'
    ),
    (
        1,
        'uid2',
        'order',
        '2020-08-26 14:00:00.0 +0000',
        120,
        TRUE,
        1,
        'empty'
    ),
    (
        2,
        'uid3',
        'order',
        '2020-08-26 15:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    );

INSERT INTO callcenter_operators.operators_shifts_events
    (
        shift_id,
        event_id,
        start,
        duration_minutes,
        description
    )
VALUES
    (
        1,
        0,
        '2020-08-26 14:00:00.0 +0000',
        90,
        ''
    ),
    (
        2,
        0,
        '2020-08-26 15:00:00.0 +0000',
        30,
        ''
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
        1,
        '2020-08-26 14:00:00.0 +0000',
        90,
        ''
    ),
    (
        2,
        '2020-08-26 15:00:00.0 +0000',
        30,
        ''
    ),
    (
        2,
        '2020-08-26 15:30:00.0 +0000',
        30,
        ''
    );
