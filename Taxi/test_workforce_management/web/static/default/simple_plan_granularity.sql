INSERT INTO callcenter_operators.skills
    (
        name,
        description,
        active
    )
VALUES
    (
        'order',
        '',
        True
    ),
    (
        'horse_archer',
        '',
        True
    ),
    (
        'hokage',
        '',
        True
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
        'mega_plan',
        'order',
        30,
        '2020-08-26 12:00:00.0 +0000'
    ),
    (
        'udmurtskie_pelmeni',
        'horse_archer',
        15,
        '2020-08-26 12:00:00.0 +0000'
    ),
    (
        'udmurtskie_pelmeni_2',
        'horse_archer',
        120,
        '2020-08-26 12:00:00.0 +0000'
    );

INSERT INTO callcenter_operators.operators_plan_records
    (
        plan_id,
        start,
        value
    )
VALUES
    (
        1,
        '2020-08-26 12:00:00.0 +0000',
        1
    ),
    (
        1,
        '2020-08-26 13:00:00.0 +0000',
        2
    ),
    (
        1,
        '2020-08-26 14:00:00.0 +0000',
        3
    ),
    (
        2,
        '2020-08-26 15:00:00.0 +0000',
        300
    );
