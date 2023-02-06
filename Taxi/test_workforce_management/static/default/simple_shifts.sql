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
        description,
        operators_schedule_types_id,
        updated_at
    )
VALUES
    (
        1,
        'uid1',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        2,
        'uid1',
        'pokemon',
        '2020-07-26 13:00:00.0 +0000',
        60,
        TRUE,
        1,
        'empty',
        1,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        3,
        'uid1',
        'pokemon',
        '2020-07-26 14:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        4,
        'uid1',
        'pokemon',
        '2020-07-26 15:00:00.0 +0000',
        60,
        TRUE,
        1,
        'empty',
        1,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        5,
        'uid2',
        'pokemon',
        '2020-07-26 16:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        6,
        'uid2',
        'pokemon',
        '2020-07-26 15:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        7,
        'uid4',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        8,
        'uid5',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        9,
        'uid3',
        'pokemon',
        '2020-10-22 00:00:00.0 +0000',
        540,
        FALSE,
        1,
        'empty',
        1,
        '2020-10-22 00:00:00.0 +0000'
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
        '2020-07-26 12:00:00.0 +0000',
        30,
        'technical'
    );
