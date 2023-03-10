INSERT INTO hiring_telephony_oktell_callback.tasks     (
        "task_id",
        "lead_id",
        "script_id",
        "line_id",
        "task_name",
        "task_state",
        "url",
        "created_at_dt",
        "expires_at_dt",
        "rots_at_dt",
        "archived_at_dt",
        "deleted_at_dt",
        "skillset",
        "is_rotten",
        "data"
    ) VALUES 
(   '1_task_already_is_rotten_1',
    'lead_id_1',
    'script_id_1',
    'line_id_1',
    'task_name_1',
    'acquired',
    'url',
    '2020-01-01'::TIMESTAMP,
    '2020-01-01'::TIMESTAMP,
    '2020-01-01'::TIMESTAMP,
    '2020-01-01'::TIMESTAMP,
    '2020-01-01'::TIMESTAMP,
    '{}'::jsonb,
    true,
    '{}'::jsonb
),
(   '2_task_should_dont_change_1',
    'lead_id_1',
    'script_id_1',
    'line_id_1',
    'task_name_1',
    'acquired',
    'url',
    '2020-01-01'::TIMESTAMP,
    '4020-01-01'::TIMESTAMP,
    '4020-01-01'::TIMESTAMP,
    '4020-01-01'::TIMESTAMP,
    '4020-01-01'::TIMESTAMP,
    '{}'::jsonb,
    false,
    '{}'::jsonb
),
(   '3_task_should_dont_change_2',
    'lead_id_1',
    'script_id_1',
    'line_id_1',
    'task_name_1',
    'processed',
    'url',
    '2014-05-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '{}'::jsonb,
    false,
    '{}'::jsonb
),
(   '4_task_should_change_1',
    'lead_id_1',
    'script_id_1',
    'line_id_1',
    'task_name_1',
    'acquired',
    'url',
    '2014-05-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '{}'::jsonb,
    true,
    '{}'::jsonb
),
(   '5_task_should_change_1',
    'lead_id_1',
    'script_id_1',
    'line_id_1',
    'task_name_1',
    'pending',
    'url',
    '2014-05-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '2020-01-16T08:28:06.801064-04:00',
    '{}'::jsonb,
    false,
    '{}'::jsonb
);
