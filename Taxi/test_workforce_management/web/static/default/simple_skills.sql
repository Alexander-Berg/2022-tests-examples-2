insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}')
on conflict do nothing;

INSERT INTO callcenter_operators.operators
    (
        yandex_uid,
        rate,
        updated_at
    )
VALUES
    (
        'uid1',
        0.5,
        '2020-08-26 00:00:00.0'
    );

INSERT INTO callcenter_operators.skills
    (
        name,
        description,
        active,
        domain,
        updated_at
    )
VALUES
    (
        'order',
        '',
        True,
        'taxi',
        '2020-10-22 12:00:00.0 +0000'
    ),
    (
        'horse_archer',
        '',
        True,
        'taxi',
        '2020-10-22 13:00:00.0 +0000'
    ),
    (
        'hokage',
        '',
        True,
        'taxi',
        '2020-10-22 14:00:00.0 +0000'
    ),
    (
        'pokemon',
        '',
        True,
        'taxi',
        '2020-10-22 14:00:00.0 +0000'
    ),
    (
        'tatarin',
        '',
        True,
        'taxi',
        '2020-10-22 14:00:00.0 +0000'
    );

INSERT INTO callcenter_operators.operators_plan_entity
    (
        name,
        skill,
        step_minutes,
        updated_at
    )
VALUES
    (
        'uid1',
        'order',
        60 * 24 * 365,
        '2020-08-26 12:00:00.0 +0000'
    ),
    (
        'tatarskoe_igo',
        'horse_archer',
        60 * 24 * 365,
        '2020-08-26 12:00:00.0 +0000'
    );

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
        '2020-08-26 12:00:00.0 +0000',
        60,
        FALSE,
        1
    );
