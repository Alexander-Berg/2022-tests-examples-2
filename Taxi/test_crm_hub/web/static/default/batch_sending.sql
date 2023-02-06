INSERT INTO crm_hub.batch_sending
(
    id,
    campaign_id,
    group_id,
    filter,
    yt_table,
    yt_test_table,
    pg_table,
    state,
    processing_chunk_size,
    use_policy,
    entity_type,
    channel,
    channel_info,
    group_type,
    created_at
)
VALUES
(
    '00000000000000000000000000000001',
    1,
    1,
    'group1',
    'yt_table',
    'yt_table_verification',
    'pg_table',
    'PROCESSING',
    0,
    False,
    'driver',
    'push',
    '{"channel_name": "driver_push"}'::JSONB,
    'testing',
    NOW()
),
(
    '00000000000000000000000000000003',
    3,
    1,
    'group3',
    'yt_table',
    'yt_table_verification',
    'pg_table',
    'PROCESSING',
    0,
    False,
    'eatsuser',
    'push',
    '{"channel_name": "eatsuser_push"}'::JSONB,
    'testing',
    NOW()
);



