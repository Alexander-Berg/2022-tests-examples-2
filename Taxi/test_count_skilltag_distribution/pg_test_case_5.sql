INSERT INTO hiring_telephony_oktell_callback.call_intervals(
    "task_id",
    "from",
    "to"
) VALUES (
    '11task_skill5',
    '2020-01-01T11:00:00+0000'::TIMESTAMP,
    '2020-01-01T15:00:00+0000'::TIMESTAMP
);

INSERT INTO hiring_telephony_oktell_callback.tasks(
    "task_id",
    "lead_id",
    "script_id",
    "line_id",
    "task_name",
    "task_state",
    "url",
    "task_state_dt",
    "created_at_dt",
    "expires_at_dt",
    "rots_at_dt",
    "archived_at_dt",
    "deleted_at_dt",
    "skillset",
    "is_rotten",
    "data"
) VALUES (
    '11task_skill5',
    'lead_id_1',
    'script_id_1',
    'line_id_1',
    'SKILL4',
    'pending',
    'url',
    '2021-10-10T12:00:00+0000'::TIMESTAMP - INTERVAL '72 HOUR',
    '2020-01-01'::TIMESTAMP,
    '2020-01-01'::TIMESTAMP,
    '2020-01-01'::TIMESTAMP,
    '2020-01-01'::TIMESTAMP,
    '2020-01-01'::TIMESTAMP,
    '["SKILL5"]'::jsonb,
    true,
    '{}'::jsonb
);
