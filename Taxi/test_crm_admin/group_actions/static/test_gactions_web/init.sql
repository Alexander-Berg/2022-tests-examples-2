INSERT INTO crm_admin.segment
(
    id,
    yql_shared_url,
    yt_table,
    mode,
    control,
    created_at
)
VALUES
(
    1,  -- id
    'yql_shared_url',
    'yt_table',
    'Share',
    20,
    '2021-01-27 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    kind,
    discount,
    state,
    ticket,
    segment_id,
    created_at
)
VALUES
(
    1,
    'campaign #1',
    'User',
    'trend',
    'kind',
    True,
    'READY',
    'ticket',
    1,
    '2020-10-26 01:00:00'
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
    ('{"channel_name": "user_push", "content": "user push text"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);

INSERT INTO crm_admin.group_v2
(
    id,
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
    1,  -- id
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
);
