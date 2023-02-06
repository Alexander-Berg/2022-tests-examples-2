INSERT INTO callcenter_operators.operators_shifts
    (
        id,
        yandex_uid,
        skill,
        start,
        duration_minutes,
        type,
        operators_schedule_types_id,
        updated_at,
        range_updated_at,
        author_yandex_uid
    )
VALUES
    (
        10,
        'uid4',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        60,
        1,
        1,
        '2020-07-26 12:15:00.0 +0000',
        '2020-07-26 12:15:00.0 +0000',
        'uid1'
    ),
    (
        11,
        'uid4',
        'pokemon',
        '2020-07-26 14:00:00.0 +0000',
        60,
        1,
        1,
        '2020-07-26 12:15:00.0 +0000',
        '2020-07-26 12:15:00.0 +0000',
        'uid1'
    ),
    (
        12,
        'uid3',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        60,
        1,
        1,
        '2020-07-26 12:15:00.0 +0000',
        '2020-07-26 12:15:00.0 +0000',
        'uid1'
    ),
    (
        13,
        'uid4',
        'pokemon',
        '2020-07-26 15:00:00.0 +0000',
        60,
        1,
        1,
        '2020-07-26 16:15:00.0 +0000',
        '2020-07-26 16:15:00.0 +0000',
        'uid1'
    );
