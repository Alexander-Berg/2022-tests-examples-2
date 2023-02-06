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
    use_policy,
    entity_type,
    group_type,
    channel,
    processing_chunk_size,
    channel_info,
    report_extra,
    created_at,
    updated_at
)
values
(
    '00000000000000000000000000000001',
    '11',
    '22',
    'group1',
    '//cmp_1_seg',
    '//cmp_1_seg_verification',
    'batch_11_22',
    'FINISHED',
    false,
    'driver',
    'testing',
    'push',
    0,
    '{"channel_name": "driver_push"}',
    '{}',
    '2020-09-15 12:00:00',
    '2020-09-15 14:00:00'
);
