INSERT INTO callcenter_operators.break_rules
    (
        alias,
        skill,
        shift_duration_minutes,
        breaks,
        domain
    )
VALUES
    (
        'long shift',
        'pokemon',
        int4range(8 * 60, 14 * 60 + 1),
        '[{"type": "technical", "min_time_without_break_minutes": 30,  "max_time_without_break_minutes": 45, "count": 4, "duration_minutes": 15}, {"type": "food", "min_time_without_break_minutes": 15,  "max_time_without_break_minutes": 300, "count": 1, "duration_minutes": 30}]',
        'taxi'
    ),
    (
        'short shift',
        'pokemon',
        int4range(2 * 60, 4 * 60 + 1),
        '[{"type": "technical", "min_time_without_break_minutes": 30,  "max_time_without_break_minutes": 45, "count": 1, "duration_minutes": 15}, {"type": "food", "min_time_without_break_minutes": 15,  "max_time_without_break_minutes": 300, "count": 1, "duration_minutes": 30}]',
        'taxi'
    );
