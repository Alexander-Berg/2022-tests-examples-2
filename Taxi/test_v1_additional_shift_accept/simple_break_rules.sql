INSERT INTO callcenter_operators.break_rules
    (
        id,
        alias,
        skill,
        shift_duration_minutes,
        breaks,
        updated_at
    )
VALUES
    (
        0,
        'awesome rule',
        'hokage',
        int4range(60, 1000),
        '[{"type": "technical", "min_time_without_break_minutes": 15,  "max_time_without_break_minutes": 1000, "count": 1, "duration_minutes": 10}]',
        '2020-10-22 12:00:00.0 +0000'
    ),
    (
        1,
        'awesome rule',
        'tatarin',
        int4range(60, 1000),
        '[{"type": "technical", "min_time_without_break_minutes": 15,  "max_time_without_break_minutes": 1000, "count": 1, "duration_minutes": 10}]',
        '2020-10-22 12:00:00.0 +0000'
    );
