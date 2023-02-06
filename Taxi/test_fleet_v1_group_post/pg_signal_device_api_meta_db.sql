INSERT INTO signal_device_api.park_device_profiles
(
    park_id,
    device_id,  
    created_at, 
    updated_at, 
    is_active,
    group_id
)
VALUES
(
    'p1',
    1,
    '2019-12-17T07:38:54',
    '2019-12-17T07:38:54',
    TRUE,
    NULL
),
(
    'p2',
    2,
    '2019-12-17T07:38:54',
    '2019-12-17T07:38:54',
    TRUE,
    NULL
),
(
    'p3',
    3,
    '2019-12-17T07:38:54',
    '2019-12-17T07:38:54',
    TRUE,
    NULL
),
(
    'p228',
    228,
    '2019-12-17T07:38:54',
    '2019-12-17T07:38:54',
    TRUE,
    NULL
);

INSERT INTO signal_device_api.device_groups (
    park_id,
    group_name,
    parent_group_id,
    idempotency_token
) VALUES (
    'p2',
    'East',
    NULL,
    'cc888693-c2c4-4f78-976f-12fc7dc32c0b'
);

INSERT INTO signal_device_api.device_groups (
    group_id,
    park_id,
    group_name,
    parent_group_id,
    idempotency_token
) VALUES (
    '29a168a6-2fe3-401d-9959-ba1b14fd4862',
    'p2',
    'South',
    NULL,
    'some_token'
),
(
    '12bb68a6-aae3-421d-9119-ca1c14fd4862',
    'p3',
    'North',
    NULL,
    'some_token2'
),
(
    'a4cc6cc6-abe3-311d-9109-a23c14fd4862',
    'p3',
    'North',
    '12bb68a6-aae3-421d-9119-ca1c14fd4862',
    'some_token5'
);

