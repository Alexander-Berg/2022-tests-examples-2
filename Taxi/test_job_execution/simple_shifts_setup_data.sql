INSERT INTO callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}')
ON CONFLICT DO NOTHING;


INSERT INTO callcenter_operators.absence_types
    (
        alias,
        description,
        domain
    )
VALUES
    (
        'vacation',
        '',
        'taxi'
    )
ON CONFLICT DO NOTHING;


INSERT INTO callcenter_operators.operators
    (
        yandex_uid
    )
VALUES
    (
        'uid1'
    ),
    (
        'uid2'
    ),
    (
        'uid3'
    )
ON CONFLICT DO NOTHING;


INSERT INTO callcenter_operators.skills
    (
        name,
        description,
        active,
        domain
    )
VALUES
    (
        'group_1_2',
        '',
        True,
        'taxi'
    ),
    (
        'skill_1',
        '',
        True,
        'taxi'
    ),
    (
        'skill_2',
        '',
        True,
        'taxi'
    ),
    (
        'skill_3',
        '',
        True,
        'taxi'
    );


TRUNCATE callcenter_operators.break_rules;
INSERT INTO callcenter_operators.break_rules
    (
        skill,
        shift_duration_minutes,
        breaks
    )
VALUES
    (
        'skill_1',
        int4range(0, 2 * 60 - 1),
        '[
            {
                "type": "technical",
                "min_time_without_break_minutes": 0,
                "max_time_without_break_minutes": 9999,
                "count": 1,
                "duration_minutes": 15
            },
            {
                "type": "lunchtime",
                "min_time_without_break_minutes": 0,
                "max_time_without_break_minutes": 9999,
                "count": 0,
                "duration_minutes": 0,
                "allowed_breaks_count_before": [0, 0]
            }
        ]'
    ),
    (
        'skill_1',
        int4range(120, 24 * 60 - 1),
        '[
            {
                "type": "technical",
                "min_time_without_break_minutes": 0,
                "max_time_without_break_minutes": 150,
                "count": 1,
                "duration_minutes": 15
            },
            {
                "type": "lunchtime",
                "min_time_without_break_minutes": 0,
                "max_time_without_break_minutes": 150,
                "count": 2,
                "duration_minutes": 30,
                "allowed_breaks_count_before": [1, 2]
            }
        ]'
    ),
    (
        'skill_2',
        int4range(0, 24 * 60 - 1),
        '[
            {
                "type": "technical",
                "min_time_without_break_minutes": 0,
                "max_time_without_break_minutes": 9999,
                "count": 0,
                "duration_minutes": 15
            },
            {
                "type": "lunchtime",
                "min_time_without_break_minutes": 0,
                "max_time_without_break_minutes": 9999,
                "count": 0,
                "duration_minutes": 0,
                "allowed_breaks_count_before": [0, 0]
            }
        ]'
    ),
    (
        'skill_3',
        int4range(12 * 60, 13 * 60 - 1),
        '[
            {
                "type": "technical",
                "min_time_without_break_minutes": 60,
                "max_time_without_break_minutes": 150,
                "count": 4,
                "duration_minutes": 15
            },
            {
                "type": "lunchtime",
                "min_time_without_break_minutes": 60,
                "max_time_without_break_minutes": 150,
                "count": 1,
                "duration_minutes": 30,
                "allowed_breaks_count_before": [2, 3]
            }
        ]'
    );


INSERT INTO callcenter_operators.skills_edges
    (
        node_from,
        node_to,
        weight
    )
VALUES
    (
        'group_1_2',
        'skill_1',
        5
    ),
    (
        'group_1_2',
        'skill_2',
        2
    );


INSERT INTO callcenter_operators.operators_plan_entity
    (
        name,
        skill,
        step_minutes
    )
VALUES
    (
        'skill_1_0',
        'skill_1',
        60
    ),
    (
        'skill_2_0',
        'skill_2',
        60
    ),
    (
        'skill_3_0',
        'skill_3',
        60
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
        '2022-02-06 21:00:00.0 +0000',
        2
    ),
    (
        1,
        '2022-02-06 22:00:00.0 +0000',
        2
    ),
    (
        1,
        '2022-02-06 23:00:00.0 +0000',
        2
    ),
    (
        1,
        '2022-02-07 00:00:00.0 +0000',
        2
    ),
    (
        2,
        '2022-02-06 21:00:00.0 +0000',
        1
    ),
    (
        2,
        '2022-02-06 22:00:00.0 +0000',
        1
    ),
    (
        2,
        '2022-02-06 23:00:00.0 +0000',
        1
    ),
    (
        2,
        '2022-02-07 00:00:00.0 +0000',
        1
    ),
    (
        2,
        '2022-02-07 01:00:00.0 +0000',
        1
    ),
    (
        2,
        '2022-02-07 02:00:00.0 +0000',
        1
    );


INSERT INTO callcenter_operators.operators_absences
    (
        type,
        yandex_uid,
        start,
        duration_minutes
    )
VALUES
    (
        1,
        'uid1',
        '2022-02-06 21:00:00.0 +0000',
        240
    ),
    (
        1,
        'uid2',
        '2022-02-07 00:00:00.0 +0000',
        240
    ),
    (
        1,
        'uid3',
        '2022-02-06 20:00:00.0 +0000',
        240
    );


INSERT INTO callcenter_operators.schedule_types
    (
        schedule_alias,
        schedule,
        first_weekend,
        start,
        duration_minutes,
        rotation_type,
        domain
    )
VALUES
    (
        '00-06/2*3',
        '{2, 3}',
        FALSE,
        '00:00',
        6 * 60,
        'sequentially',
        'taxi'
    ),
    (
        '2/3 | 21-09',
        '{2, 3}',
        FALSE,
        '18:00',
        12 * 60,
        'sequentially',
        'taxi'
    );


TRUNCATE callcenter_operators.operators_schedule_types CASCADE;
INSERT INTO callcenter_operators.operators_schedule_types
    (
        id,
        yandex_uid,
        schedule_type_id,
        starts_at,
        expires_at
    )
VALUES
    (
        1,
        'uid1',
        1,
        '2022-02-07 00:00:00.0 +0000',
        NULL
    ),
    (
        2,
        'uid2',
        1,
        '2022-02-07 00:00:00.0 +0000',
        NULL
    ),
    (
        3,
        'uid3',
        1,
        '2022-02-07 00:00:00.0 +0000',
        NULL
    );


INSERT INTO callcenter_operators.operators_schedule_type_skills
    (
        operators_schedule_types_id,
        skill,
        is_primary
    )
VALUES
    (
        1,
        'skill_1',
        TRUE
    ),
    (
        1,
        'skill_2',
        FALSE
    ),
    (
        2,
        'skill_1',
        TRUE
    ),
    (
        2,
        'skill_2',
        TRUE
    ),
    (
        3,
        'skill_1',
        FALSE
    ),
    (
        3,
        'skill_2',
        FALSE
    );
