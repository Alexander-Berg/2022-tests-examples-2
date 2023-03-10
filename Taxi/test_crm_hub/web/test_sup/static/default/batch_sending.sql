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
    start_id,
    created_at
)
VALUES
(
    '00000000000000000000000000000001',
    1,
    1,
    'Default',
    'yt_table',
    'yt_table_verification',
    'pg_table',
    'PROCESSING',
    0,
    False,
    'geo',
    'push',
    '{"channel_name": "geo_push"}'::JSONB,
    'testing',
    0,
    NOW()
);
