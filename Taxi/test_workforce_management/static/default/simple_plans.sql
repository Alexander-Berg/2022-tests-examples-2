INSERT INTO callcenter_operators.operators_plan_entity
    (
        name,
        skill,
        step_minutes,
        updated_at
    )
VALUES
    (
        'pokemon_0',
        'pokemon',
        60,
        '2020-07-01 00:00:00.0 +0000'
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
        '2020-06-01 12:00:00.0 +0000',
        1
    ),
    (
        1,
        '2020-07-01 12:00:00.0 +0000',
        1
    ),
    (
        1,
        '2020-07-01 15:00:00.0 +0000',
        2
    ),
    (
        1,
        '2020-07-01 16:00:00.0 +0000',
        2
    ),
    (
        1,
        '2020-07-01 17:00:00.0 +0000',
        4
    );
