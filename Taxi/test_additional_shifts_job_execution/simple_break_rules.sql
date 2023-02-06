INSERT INTO callcenter_operators.skills
    (
        name,
        description,
        active,
        updated_at
    )
VALUES
    (
        'pokemon',
        '',
        True,
        '2020-10-22 13:00:00.0 +0000'
    )
ON CONFLICT DO NOTHING;

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
        'pokemon',
        int4range(60, 120),
        '[{"type": "technical", "min_time_without_break_minutes": 15,  "max_time_without_break_minutes": 100, "count": 1, "duration_minutes": 10}]',
        '2020-10-22 12:00:00.0 +0000'
    ),
    (
        1,
        'awesome rule',
        'pokemon',
        int4range(120, 1000),
        '[{"type": "technical", "min_time_without_break_minutes": 15,  "max_time_without_break_minutes": 100, "count": 0, "duration_minutes": 10}]',
        '2020-10-22 12:00:00.0 +0000'
    ),
    (
        2,
        'awesome rule',
        'pokemon',
        int4range(30, 60),
        '[{"type": "technical", "min_time_without_break_minutes": 15,  "max_time_without_break_minutes": 30, "count": 1, "duration_minutes": 5}]',
        '2020-10-22 12:00:00.0 +0000'
    ),
    (
        3,
        'awesome rule',
        'hokage',
        int4range(120, 1000),
        '[{"type": "technical", "min_time_without_break_minutes": 15,  "max_time_without_break_minutes": 30, "count": 1, "duration_minutes": 5}]',
        '2020-10-22 12:00:00.0 +0000'
    );
