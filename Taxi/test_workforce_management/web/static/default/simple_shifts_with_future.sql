insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;

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
        'pokemon',
        '2024-09-26 15:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        3
    ),
    (
        'uid3',
        'pokemon',
        '2020-09-26 15:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        3
    ),
    (
        'uid3',
        'pokemon',
        '2023-08-15 15:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        3
    ),
    (
        'uid3',
        'pokemon',
        '2023-08-12 15:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        3
    ),
    (
        'uid3',
        'hokage',
        '2023-08-16 15:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        3
    );
