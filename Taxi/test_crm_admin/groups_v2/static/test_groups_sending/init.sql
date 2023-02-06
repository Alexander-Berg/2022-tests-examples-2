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
    'segment#1 shared link',
    'path/to/segment_1',
    ('{
        "size": 2000,
        "distribution": [
            {
                "city": "Moscow",
                "locales": [
                    { "name": "ru", "value": 1000 },
                    { "name": "en", "value": 500 }
                ]
            },
            {
                "city": "Saint Petersburg",
                "locales": [
                    { "name": "ru", "value": 500 },
                    { "name": "en", "value": 1000 }
                ]
            }
        ]
    }')::jsonb,
    'Share',
    20,
    '2020-06-09 01:00:00'
);

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
    'creative 1',
    ('{"channel_name": "user_push", "content": "push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);

INSERT INTO crm_admin.group_v2
(
    creative_id,
    segment_id,
    name,
    type,
    params,
    sending_stats,
    computed,
    state,
    send_at,
    created_at,
    updated_at
)
VALUES
(
    1,
    1,
    'share_group_1',
    'SHARE',
    ('{"share": 20}')::jsonb,
    ('{"denied": 104, "failed": 102, "sent": 100, "skipped": 103}')::jsonb,
    ('{"total": 510}')::jsonb,
    'EFFICIENCY_ANALYSIS',
    '2019-11-20T01:00:00',
    '2020-06-09 01:00:00',
    '2020-06-09 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
    name,
    segment_id,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    global_control,
    ticket,
    created_at,
    efficiency
)
VALUES
(
    1,
    'campaing #1',
    1,
    'User',
    'campaign #1 trend',
    'campaign #1 kind',
    True,
    'GROUPS_PRECALCULATING',
    'user1',
    True,
    'ticket #1',
    '2020-04-01 01:00:00',
    true
);
