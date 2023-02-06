insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"distribute_breaks_inside": true}'), (2, 'additional', '{"distribute_breaks_inside": true}')
on conflict do nothing;

insert into callcenter_operators.shift_events (id, alias, description, properties)
VALUES (0, 'tutoring', 'tutor tutoring students', '{"distribute_breaks_inside": true}'),
       (1, 'with_breaks', 'training with its own breaks inside', '{"distribute_breaks_inside": false}')
on conflict do nothing;

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
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    ),
    (
        'uid1',
        'pokemon',
        '2020-07-26 13:00:00.0 +0000',
        60,
        TRUE,
        1,
        'empty'
    ),
    (
        'uid1',
        'pokemon',
        '2020-07-26 14:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    ),
    (
        'uid1',
        'pokemon',
        '2020-07-26 15:00:00.0 +0000',
        60,
        TRUE,
        1,
        'empty'
    ),
    (
        'uid2',
        'pokemon',
        '2020-07-26 16:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    ),
    (
        'uid2',
        'pokemon',
        '2020-07-26 15:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'
    );
