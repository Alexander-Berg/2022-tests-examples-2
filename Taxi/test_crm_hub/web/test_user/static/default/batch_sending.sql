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
    'group2',
    'yt_table',
    'yt_table_verification',
    'pg_table',
    'PROCESSING',
    0,
    False,
    'user',
    'push',
    '{"channel_name": "user_push"}'::JSONB,
    'testing',
    NOW()
);

