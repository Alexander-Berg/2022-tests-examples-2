INSERT INTO crm_admin.segment
(
    id,
    yql_shared_url,
    yt_table,
    mode,
    control,
    created_at,
    aggregate_info
)
VALUES
(
    1,
    'segment#1 shared link',
    'path/to/segment_1',
    'Share',
    20,
    '2020-06-09 01:00:00',
    '{}'::jsonb
);

INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    name,
    specification,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    ticket,
    creative,
    settings,
    segment_stats_status,
    created_at
)
VALUES
(
    1,
    1,
    'Первая кампания',
    'Описание первой кампании',
    'User',
    'Направление или тип первой кампании',
    'Тип или подтип первой кампании',
    True,
    'SEGMENT_CALCULATING',
    'user1',
    'Тикет1',
    'Первый креатив',
    ('[]')::jsonb,
    '{}'::jsonb,
    '2020-03-20 01:00:00'
);

INSERT INTO crm_admin.target
(
    id,
    owner,
    name,
    label,
    description,
    is_available,
    is_important,
    audiences,
    apply_conditions,
    control_settings,
    const_salt,
    created_at,
    updated_at
)
VALUES
(
    1,
    'trusienkodv',
    'target_1',
    'target_1',
    'description_1',
    TRUE,
    TRUE,
    '{"User"}',
    '{}'::jsonb,
    '{"is_control_enabled": true, "is_control_active": true, "track_all": true}'::jsonb,
    'const_salt1',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    2,
    'trusienkodv',
    'target_2',
    'target_2',
    'description_2',
    TRUE,
    TRUE,
    '{"User"}',
    '{}'::jsonb,
    '{"is_control_enabled": true, "is_control_active": true, "track_all": true}'::jsonb,
    'const_salt2',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    3,
    'trusienkodv',
    'target_3',
    'target_3',
    'description_3',
    TRUE,
    TRUE,
    '{"User"}',
    '{}'::jsonb,
    '{"is_control_enabled": true, "is_control_active": true, "track_all": true}'::jsonb,
    'const_salt3',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
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
),
(
    2,
    'trusienkodv',
    1,
    '{"mechanism": "exp3", "salt": "period_2_salt", "control_percentage": 3, "key": "user_phone_id"}'::jsonb,
    4,
    '2020-03-20 03:00:00',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    3,
    'trusienkodv',
    1,
    '{"mechanism": "exp3", "salt": "period_3_salt", "control_percentage": 5, "key": "user_phone_id"}'::jsonb,
    6,
    '2020-03-20 02:00:00',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    4,
    'trusienkodv',
    1,
    '{"mechanism": "exp3", "salt": "period_4_salt", "control_percentage": 7, "key": "user_phone_id"}'::jsonb,
    8,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    5,
    'trusienkodv',
    2,
    '{"mechanism": "exp3", "salt": "period_5_salt", "control_percentage": 9, "key": "user_id"}'::jsonb,
    10,
    '2020-03-20 02:00:00',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    6,
    'trusienkodv',
    2,
    '{"mechanism": "murmur", "salt": "period_6_salt", "control_percentage": 11, "key": "user_id"}'::jsonb,
    12,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    7,
    'trusienkodv',
    3,
    '{"mechanism": "murmur", "salt": "period_7_salt", "control_percentage": 13, "key": "user_id"}'::jsonb,
    14,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
)
;

INSERT INTO crm_admin.campaign_target_connection
(
    campaign_id,
    target_id,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    1,
    2,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
),
(
    1,
    3,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
)
;
