insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;

insert into callcenter_operators.shift_events (id, alias, description, properties, updated_at)
VALUES (1, 'training', 'no matter train muscles or brain', '{"distribute_breaks_inside": true, "is_training": false}', '2020-11-16 14:10:00.0'),
       (2, 'with_breaks', 'training with its own breaks inside', '{"distribute_breaks_inside": false, "is_training": true}',
        '2020-11-16 14:10:00.0');

INSERT INTO callcenter_operators.operators_shifts
    (
        yandex_uid,
        skill,
        start,
        duration_minutes,
        frozen,
        type,
        description,
        operators_schedule_types_id,
        author_yandex_uid
    )
VALUES
    (
        'uid1',
        NULL,
        '2020-07-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1,
        'uid1'
    ),
    (
        'uid1',
        'pokemon',
        '2020-07-26 13:00:00.0 +0000',
        60,
        TRUE,
        1,
        'empty',
        1,
        'uid1'
    ),
    (
        'uid1',
        'pokemon',
        '2020-07-26 14:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1,
        'uid1'
    ),
    (
        'uid1',
        'pokemon',
        '2020-07-26 15:00:00.0 +0000',
        60,
        TRUE,
        1,
        'empty',
        1,
        'uid1'
    ),
    (
        'uid2',
        'pokemon',
        '2020-07-26 16:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1,
        'uid1'
    ),
    (
        'uid2',
        'pokemon',
        '2020-07-26 15:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1,
        'uid1'
    );


INSERT INTO callcenter_operators.operators_breaks
(shift_id,
 start,
 duration_minutes,
 type)
VALUES (1,
        '2020-07-26 12:00:00.0 +0000',
        30,
        'technical'),
       (1,
        '2020-07-26 12:30:00.0 +0000',
        30,
        'technical');

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

