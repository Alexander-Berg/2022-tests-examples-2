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
    )
ON CONFLICT (name) DO NOTHING;

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
        60,
        '2020-08-26 12:00:00.0 +0000'
    ),
    (
        'tatarskoe_igo',
        'horse_archer',
        60 * 24 * 365,
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
        30
    ),
    (
        1,
        '2020-08-26 13:00:00.0 +0000',
        300
    ),
    (
        1,
        '2020-08-26 14:00:00.0 +0000',
        3000
    ),
    (
        1,
        '2020-08-26 15:00:00.0 +0000',
        30000
    );
