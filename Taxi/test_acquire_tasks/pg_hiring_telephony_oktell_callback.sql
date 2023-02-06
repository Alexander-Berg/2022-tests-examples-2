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
        "data",
        "priority"
    ) VALUES (
    'task_id_1',
    'lead_id_1',
    'script_id_1',
    'line_id_1',
    'common_skilltag',
    'pending',
    'url',
    '2020-01-01'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    false,
    true,
    '["common_skilltag"]'::jsonb,
    '{"personal": [{"type": "phones", "value": "phone_pd_id", "field_name":
    "phone", "is_personal_id": true}]}'::jsonb,
    3
),(
    'task_id_2',
    'lead_id_2',
    'script_id_2',
    'line_id_2',
    'common_skilltag',
    'pending',
    'url',
    '2020-01-01'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    false,
    true,
    '["common_skilltag"]'::jsonb,
    '{"personal": [{"type": "phones", "value": "phone_pd_id", "field_name":
    "phone", "is_personal_id": true}]}'::jsonb,
    1
),(
    'task_id_3',
    'lead_id_3',
    'script_id_3',
    'line_id_3',
    'common_skilltag',
    'pending',
    'url',
    '2020-01-01'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    false,
    true,
    '["common_skilltag"]'::jsonb,
    '{"personal": [{"type": "phones", "value": "phone_pd_id", "field_name":
    "phone", "is_personal_id": true}]}'::jsonb,
    2
),(
    'task_id_another',
    'lead_id_another',
    'script_id_another',
    'line_id_another',
    'another_skilltag',
    'pending',
    'url',
    '2020-01-01'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    '2020-01-16'::TIMESTAMP,
    false,
    true,
    '["another_skilltag"]'::jsonb,
    '{"personal": [{"type": "phones", "value": "phone_pd_id", "field_name":
    "phone", "is_personal_id": true}]}'::jsonb,
    3
);

INSERT INTO hiring_telephony_oktell_callback.call_intervals (
       "task_id",
       "from",
       "to"
) VALUES (
  'task_id_1',
  '2000-01-01'::TIMESTAMP,
  '3000-01-01'::TIMESTAMP
),(
  'task_id_2',
  '2000-01-01'::TIMESTAMP,
  '3000-01-01'::TIMESTAMP
),(
  'task_id_3',
  '2000-01-01'::TIMESTAMP,
  '3000-01-01'::TIMESTAMP
),(
  'task_id_another',
  '2000-01-01'::TIMESTAMP,
  '3000-01-01'::TIMESTAMP
);
