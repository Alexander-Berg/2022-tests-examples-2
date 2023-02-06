INSERT INTO callcenter_operators.skills
    (
        name,
        description,
        active,
        updated_at,
        domain
    )
VALUES
    (
        'order',
        '',
        True,
        '2020-10-22 12:00:00.0 +0000',
        'taxi'
    ),
    (
        'horse_archer',
        '',
        True,
        '2020-10-22 13:00:00.0 +0000',
        'taxi'
    ),
    (
        'pokemon',
        '',
        True,
        '2020-10-22 13:00:00.0 +0000',
        'taxi'
    )
ON CONFLICT DO NOTHING;

INSERT INTO callcenter_operators.break_rules
    (
        id,
        alias,
        skill,
        shift_duration_minutes,
        breaks,
        updated_at,
        domain
    )
VALUES
    (
        0,
        'awesome rule',
        'pokemon',
        int4range(60, 120),
        '[{"type": "technical", "min_time_without_break_minutes": 10,  "max_time_without_break_minutes": 100, "count": 1, "duration_minutes": 10}]',
        '2020-10-22 12:00:00.0 +0000',
        'taxi'
    ),
    (
        1,
        'awesome rule #2',
        'droid',
        int4range(60, 120),
        '[{"type": "technical", "min_time_without_break_minutes": 10,  "max_time_without_break_minutes": 100, "count": 2, "duration_minutes": 5}, {"type": "lunchtime", "min_time_without_break_minutes": 10,  "max_time_without_break_minutes": 100, "count": 1, "duration_minutes": 10}]',
        '2020-10-22 12:00:00.0 +0000',
        'taxi'
    )
