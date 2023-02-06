insert into callcenter_operators.shift_types (id, alias, properties)
values (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;

insert into callcenter_operators.shift_events (id, alias, description)
values (1, 'tutoring', 'tutor tutoring students'),
(2, 'training', 'no matter train muscles or brain');


insert into callcenter_operators.operators_shifts
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
values
    (
        1,
        'uid1',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    ),
    (
        2,
        'uid1',
        'pokemon',
        '2020-07-26 13:00:00.0 +0000',
        60,
        TRUE,
        1,
        'empty'
    ),
    (
        3,
        'uid1',
        'pokemon',
        '2020-07-26 14:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    ),
    (
        4,
        'uid1',
        'pokemon',
        '2020-07-26 15:00:00.0 +0000',
        60,
        TRUE,
        1,
        'empty'
    ),
    (
        5,
        'uid2',
        'droid',
        '2020-07-26 16:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    ),
    (
        6,
        'uid2',
        'droid',
        '2020-07-26 15:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    ),
    (
        7,
        'uid3',
        'pokemon',
        '2020-07-26 00:00:00.0+00',
        6000,
        FALSE,
        1,
        'empty'
    ),
    (
        8,
        'uid3',
        'pokemon',
        '2023-08-01 00:00:00.0+00',
        60,
        FALSE,
        1,
        'empty'
    ),
    (
        9,
        'uid3',
        'hokage',
        '2023-08-01 01:00:00.0+00',
        60,
        FALSE,
        1,
        'empty'
    );

insert into callcenter_operators.operators_breaks
    (
        shift_id,
        start,
        duration_minutes,
        type
    )
values
    (
        1,
        '2020-07-26 12:00:00.0 +0000',
        30,
        'technical'
    );

insert into callcenter_operators.operators_shifts_events
    (
            shift_id,
            event_id,
            start,
            duration_minutes,
            description
    )
values
    (
        1,
        1,
        '2020-07-26 12:30:00.0 +0000',
        30,
        'technical'
    ),
    (
        5,
        2,
        '2020-07-26 16:00:00.0 +0000',
        15,
        'technical'
    );


INSERT INTO callcenter_operators.operators_shifts_segments
(shift_id,
 start,
 duration_minutes,
 skill,
 description)
VALUES (1,
        '2020-07-26 12:00:00.0 +0000',
        30,
        'pokemon',
        'awesome description'),
       (1,
        '2020-07-26 12:30:00.0 +0000',
        30,
        'pokemon',
        NULL);

