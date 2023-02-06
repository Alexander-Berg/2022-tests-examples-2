INSERT INTO callcenter_operators.operators_absences
    (
        id,
        type,
        yandex_uid,
        start,
        duration_minutes,
        updated_at,
        author_yandex_uid
    )
VALUES
    (
        0,
        1,
        'uid1',
        '2020-07-27 18:00:00.0 +0000',
        60,
        '2020-07-27 18:00:00.0 +0000',
        'uid1'
    ),
    (
        1,
        1,
        'uid1',
        '2020-07-27 21:00:00.0 +0000',
        60,
        '2020-07-27 21:00:00.0 +0000',
        NULL
    ),
    (
        2,
        1,
        'uid2',
        '2020-07-27 12:00:00.0 +0000',
        60,
        '2020-07-27 12:00:00.0 +0000',
        NULL
    );
