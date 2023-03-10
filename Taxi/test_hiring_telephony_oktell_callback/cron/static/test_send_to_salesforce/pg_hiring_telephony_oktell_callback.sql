INSERT INTO hiring_telephony_oktell_callback.tasks (
        "task_id",
        "lead_id",
        "script_id",
        "line_id",
        "task_name",
        "task_state",
        "url",
        "task_state_dt",
        "created_at_dt",
        "updated_at_dt",
        "expires_at_dt",
        "rots_at_dt",
        "archived_at_dt",
        "deleted_at_dt",
        "skillset",
        "is_expired",
        "data",
        "csat",
        "result_data",
        "extra"
    ) VALUES (
    'task_to_send_1',
    'lead_id_1',
    'script_id_1',
    'line_id_1',
    'task_name_1',
    'acquired',
    'url',
    '2020-01-01'::TIMESTAMP,
    '2020-01-01'::TIMESTAMP,
    '2020-01-02'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '{}'::jsonb,
    true,
    '{}'::jsonb,
    5,
    '{"operator_id": "9a5ede2539154fb7b00ed0ceb85843a5", "call_result": "call_successful", "call_result_dt": "2020-01-20T13:44:55.098000"}'::jsonb,
    '{}'::jsonb
),
(
    'task_to_send_2',
    'lead_id_2',
    'script_id_2',
    'line_id_2',
    'task_name_2',
    'acquired',
    'url',
    '2020-01-01'::TIMESTAMP,
    '2020-01-01'::TIMESTAMP,
    '2020-01-03'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '{}'::jsonb,
    true,
    '{}'::jsonb,
    4,
    '{}'::jsonb,
    '{"e":["e"]}'::jsonb
);
