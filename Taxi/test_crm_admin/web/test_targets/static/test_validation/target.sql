INSERT INTO crm_admin.target
(
    owner,
    name,
    label,
    audiences,
    control_settings,
    const_salt,
    created_at,
    updated_at
)
VALUES
(
    'owner',
    'name',
    'target_1',
    '{"Driver"}'::text[],
    '{"is_control_active": true, "is_control_enabled": true, "track_all": false}',
    'salt',
    '2021-03-12 01:00:00',
    '2021-03-12 01:00:00'
);

INSERT INTO crm_admin.period
(
    id,
    owner,
    target_id,
    control,
    previous_control_percentage,
    start_at,
    created_at,
    updated_at
)
VALUES
(
    1,
    'trusienkodv',
    1,
    '{"mechanism": "murmur", "salt": "period_1_salt", "control_percentage": 1, "key": "user_phone_id"}'::jsonb,
    2,
    '2020-03-20 04:00:00',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
);
