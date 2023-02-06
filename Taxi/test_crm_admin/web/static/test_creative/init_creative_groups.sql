INSERT INTO crm_admin.creative
(
    id,
    name,
    params,
    created_at,
    updated_at
)
VALUES
(
    1,  -- id
    'creative 10',
    ('{"channel_name": "driver_push", "code": 100, "content": "Hello!"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
),
(
    2,  -- id
    'creative 10',
    ('{"channel_name": "driver_push", "code": 100, "content": "Hello!"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);

INSERT INTO crm_admin.segment
(
    id,
    yql_shared_url,
    yt_table,
    aggregate_info,
    mode,
    control,
    created_at
)
VALUES
(
    1,
    'test1_yql_shred_link',
    'test1_yt_table',
    ('{
        "size": 2000,
        "distribution": [
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            },
            {
                "city": "Москва",
                "locales": [
                    { "name": "RU", "value": 1000 },
                    { "name": "CZ", "value": 500 }
                ]
            }
        ],
        "policy": {
            "PUSH": {
                "size": 1800,
                "blocked_size": 200
            }
        }
    }')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
),
(
    2,
    'test2_yql_shred_link',
    'test2_yt_table',
    ('{"size": 2000}')::jsonb,
    'Filter',
    10,
    '2019-11-20 01:00:00'
);

INSERT INTO crm_admin.group_v2
(
    creative_id,
    segment_id,
    name,
    state,
    type,
    params,
    sending_stats,
    computed,
    efficiency_time,
    efficiency_date,
    send_at,
    yql_shared_url,
    created_at,
    updated_at
)
VALUES
(
    -- id: 1
    1,
    1,
    'share_group_1',
    'NEW',
    'SHARE',
    ('{
        "share": 20
    }')::jsonb,
    null,
    null,
    '{"01:00", "02:00"}',
    '{"2021-01-01", "2021-01-02"}',
    '2019-11-20T01:00:00',
    'yql_shared_url',
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 2
    1,
    1,
    'share_group_2',
    'PLANNED',
    'SHARE',
    ('{
        "share": 10
    }')::jsonb,
    ('{}')::jsonb,
    null,
    '{"02:00", "03:00"}',
    '{"2021-01-02", "2021-01-03"}',
    '2019-11-20T01:00:00',
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
),
(
    -- id: 3
    2,
    2,
    'share_group_3',
    'NEW',
    'SHARE',
    ('{
        "computed_share": 10,
        "share": 10
    }')::jsonb,
    ('{"sent": 100, "failed": 50, "planned": 180, "skipped": 30, "finished_at": "2021-01-20T16:40:00+03:00"}')::jsonb,
    null,
    '{"03:00", "04:00"}',
    '{"2021-01-03", "2021-01-04"}',
    '2019-11-20T01:00:00',
    null,
    '2019-11-20 01:00:00',
    '2019-11-20 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    discount,
    state,
    salt,
    created_at,
    segment_id
)
VALUES
(
    1,
    'name',
    'User',
    'trend',
    True,
    'NEW',
    'salt',
    '2021-03-12 01:00:00',
    1
),
(
    2,
    'name',
    'User',
    'trend',
    True,
    'NEW',
    'salt',
    '2021-03-12 01:00:00',
    2
);

INSERT INTO crm_admin.campaign_creative_connection
(
    id,
    campaign_id,
    creative_id,
    created_at
)
VALUES
(
    1,
    1,
    1,
    '2021-03-12 01:00:00'
),
(
    2,
    2,
    2,
    '2021-03-12 01:00:00'
);
