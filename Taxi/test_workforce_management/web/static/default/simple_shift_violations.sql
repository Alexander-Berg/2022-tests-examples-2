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
        7,
        'uid3',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        120,
        FALSE,
        1,
        'empty',
        1,
        '2020-07-26 12:00:00.0 +0000'
    )
    ON CONFLICT DO NOTHING;

INSERT INTO callcenter_operators.operators_shifts_violations
    (
        yandex_uid,
        state_type,
        start,
        duration_minutes,
        finish,
        shift_id,
        updated_at
    )
VALUES
    (
        'uid1',
        'late',
        '2020-07-26 12:00:00.0 +0000',
        60,
        '2020-07-26 13:00:00.0 +0000',
        1,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        'uid1',
        'late',
        '2020-07-26 13:00:00.0 +0000',
        60,
        '2020-07-26 14:00:00.0 +0000',
        2,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        'uid1',
        'late',
        '2020-07-26 14:00:00.0 +0000',
        60,
        '2020-07-26 15:00:00.0 +0000',
        3,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        'uid1',
        'late',
        '2020-07-26 15:00:00.0 +0000',
        60.12372311666667,
        '2020-07-26 16:00:7.423387 +0000',
        4,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        'uid2',
        'absent',
        '2020-07-26 12:00:00.0 +0000',
        240,
        '2020-07-26 16:00:00.0 +0000',
        6,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        'uid2',
        'late',
        '2020-07-26 16:00:00.0 +0000',
        NULL,
        NULL,
        5,
        '2020-07-26 12:00:00.0 +0000'
    ),
    (
        'uid3',
        'absent',
        '2020-07-26 12:00:00.0 +0000',
        NULL,
        NULL,
        7,
        '2020-07-26 12:00:00.0 +0000'
    );
