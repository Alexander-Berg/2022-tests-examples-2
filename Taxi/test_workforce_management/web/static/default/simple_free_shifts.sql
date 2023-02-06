insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}')
on conflict do nothing;
INSERT INTO callcenter_operators.operators_shifts
    (
        yandex_uid,
        skill,
        start,
        duration_minutes,
        frozen,
        type
    )
VALUES
    (
        'uid1',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        60,
        FALSE,
        1
    ),
    (
        'uid1',
        'pokemon',
        '2020-07-26 13:00:00.0 +0000',
        60,
        TRUE,
        1
    ),
    (
        'uid1',
        'pokemon',
        '2020-07-26 14:00:00.0 +0000',
        60,
        FALSE,
        1
    ),
    (
        'uid1',
        'pokemon',
        '2020-07-26 15:00:00.0 +0000',
        60,
        TRUE,
        1
    ),
    (
        'uid4',
        'pokemon',
        '2020-08-01 15:00:00.0 +0000',
        60,
        FALSE,
        1
    );
