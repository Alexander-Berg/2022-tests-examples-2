INSERT INTO crm_hub.batch_sending (
    id,
    campaign_id,
    group_id,
    start_id,
    pg_table,
    filter,
    yt_table,
    yt_test_table,
    state,
    entity_type,
    channel,
    channel_info,
    group_type,
    processing_chunk_size,
    use_policy,
    created_at,
    updated_at
)
VALUES
(
    '00000000000000000000000000000001',
    1,
    1,
    0,
    'pg1',
    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000002',
    2,
    2,
    0,
    'pg2',
    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000003',
    3,
    3,
    0,
    'pg3',
    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000004',
    4,
    4,
    0,
    'pg4',
    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000005',
    5,
    5,
    0,
    'pg4',
    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000006',
    6,
    6,
    0,
    'pg4',
    'filter',
    'yt_table',
    'yt_test_table',
    'PROCESSING',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000007',
    7,
    7,
    0,
    'pg4',
    'filter',
    'yt_table',
    'yt_test_table',
    'NEW',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000008',
    8,
    8,
    0,
    'pg4',
    'filter',
    'yt_table',
    'yt_test_table',
    'FINISHED',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000009',
    9,
    9,
    0,
    'pg4',
    'filter',
    'yt_table',
    'yt_test_table',
    'PROCESSING',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
),
(
    '00000000000000000000000000000010',
    10,
    10,
    0,
    'pg4',
    'filter',
    'yt_table',
    'yt_test_table',
    'ERROR',
    'driver',
    'push',
    '{"ttl": 100, "code": 1300, "flags": [], "content": "content", "channel_name": "driver_push", "need_notification": true}',
    'control',
    100,
    True,
    '2020-12-04 00:10:00',
    '2021-01-20 14:21:00'
);


INSERT INTO crm_hub.multi_sending_parts
(
    multi_sending_id,
    batch_sending_id,
    created_at
)
VALUES
(
    '00000000000000000000000000000001',
    '00000000000000000000000000000001',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000001',
    '00000000000000000000000000000002',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000002',
    '00000000000000000000000000000003',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000002',
    '00000000000000000000000000000004',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000003',
    '00000000000000000000000000000005',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000003',
    '00000000000000000000000000000006',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000003',
    '00000000000000000000000000000007',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000004',
    '00000000000000000000000000000008',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000004',
    '00000000000000000000000000000009',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000004',
    '00000000000000000000000000000010',
    now() AT TIME ZONE 'UTC'
);
