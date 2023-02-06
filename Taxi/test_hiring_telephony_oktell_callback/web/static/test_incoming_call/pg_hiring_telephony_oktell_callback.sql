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
        "is_stopped",
        "is_sent_to_recall",
        "skillset",
        "data"
    ) VALUES (
    'task_id_1',
    'lead_id_1',
    'script_id_1',
    'line_id_1',
    'incomming_call',
    'pending',
    'url',
    '2020-01-01'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    false,
    true,
    '["incomming_call"]'::jsonb,
    '{"personal": [{"type": "phones", "value": "phone_pd_id", "field_name": "phone", "is_personal_id": true}]}'::jsonb
);

INSERT INTO hiring_telephony_oktell_callback.call_intervals (
       "task_id",
       "from",
       "to"
) VALUES (
  'task_id_1',
  '2000-01-01'::TIMESTAMP,
  '3000-01-01'::TIMESTAMP
);
