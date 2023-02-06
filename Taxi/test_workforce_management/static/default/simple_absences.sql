INSERT INTO callcenter_operators.absence_types
    (
        alias,
        description,
        updated_at,
        domain
    )
VALUES
    (
        'vacation',
        '',
        '2020-10-22 12:00:00.0 +0000',
        'taxi'
    ),
    (
        'other',
        '',
        '2020-10-22 12:00:00.0 +0000',
        'taxi'
    );


INSERT INTO callcenter_operators.operators_absences
    (
        id,
        type,
        yandex_uid,
        start,
        duration_minutes
    )
VALUES
    (
        0,
        1,
        'uid2',
        '2020-08-05 14:00:00.0 +0000',
        600
    );
