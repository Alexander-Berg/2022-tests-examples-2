INSERT INTO crm_hub.batch_sending (
    id,
    campaign_id,
    group_id,
    filter,
    yt_table,
    yt_test_table,
    pg_table,
    state,
    created_at,
    entity_type,
    group_type,
    channel,
    channel_info,
    processing_chunk_size,
    use_policy
)
VALUES
(
    '00000000000000000000000000000001',
    1,
    1,
    'filter',
    'yt_table',
    'yt_test_table',
    'pg_table',
    'NEW',
    '2020-08-18 01:00:00',
    'user',
    'testing',
    'promo',
    '{"channel_name": "user_promo"}',
    10,
    False
),
(
    '00000000000000000000000000000002',
    2,
    2,
    'filter',
    'yt_table',
    'yt_test_table',
    'pg_table',
    'PROCESSING',
    '2020-08-18 01:00:00',
    'driver',
    'testing',
    'legacywall',
    '{"channel_name": "driver_wall"}',
    10,
    False
),
(
    '00000000000000000000000000000003',
    1,
    3,
    'filter',
    'yt_table',
    'yt_test_table',
    'pg_table',
    'FINISHED',
    '2020-08-18 01:00:00',
    'user',
    'testing',
    'sms',
    '{"channel_name": "user_sms"}',
    10,
    False
);

INSERT INTO crm_hub.batch_sending (
    id,
    campaign_id,
    group_id,
    filter,
    yt_table,
    yt_test_table,
    pg_table,
    state,
    entity_type,
    group_type,
    processing_chunk_size,
    use_policy,
    extra_data,
    extra_data_path,
    created_at,
    subfilters,
    sending_stats,
    start_id,
    replication_state,
    verify,
    control,
    group_name,
    actions
) VALUES
(
    '00000000000000000000000000000004',
    3,
    4,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_test_table',
    '',
    'user',
    'testing',
    30,
    TRUE,
    '{}'::jsonb,
    '//home/taxi-crm/cmp_extra_data',
    NOW() AT TIME ZONE 'UTC',
    '{}'::jsonb,
    '{}'::jsonb,
    0,
    'NEW',
    FALSE,
    FALSE,
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "user_promo",
                            "content": "promo_id", "ticket": "ticket"}
        },
        {
            "action_name": "policy",
            "channel": "promo"
        }
    ]')::jsonb
),
(
    '00000000000000000000000000000005',
    3,
    5,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'sending_test_table',
    '',
    'user',
    'testing',
    30,
    TRUE,
    '{}'::jsonb,
    '//home/taxi-crm/cmp_extra_data',
    NOW() AT TIME ZONE 'UTC',
    '{}'::jsonb,
    '{}'::jsonb,
    0,
    'NEW',
    FALSE,
    FALSE,
    'group_name',
    ('[
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "user_promo",
                            "content": "promo_id", "ticket": "ticket"}
        },
        {
            "action_name": "channel",
            "channel_info": {"channel_name": "user_promo",
                            "content": "promo_id", "ticket": "ticket"}
        },
        {
            "action_name": "policy",
            "channel": "promo"
        }
    ]')::jsonb
);
