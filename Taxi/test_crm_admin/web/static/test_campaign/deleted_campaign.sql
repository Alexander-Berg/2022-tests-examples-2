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
    1,
    '#1 yql_shared_url',
    '#1 yt_table',
    'Share',
    20,
    '2020-05-16 01:00:00'
)
;

INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    name,
    entity_type,
    trend,
    discount,
    state,
    created_at,
    deleted_at
)
VALUES
(
    1,
    1,
    'campaign #1',
    'User',
    '#1 trend',
    True,
    'NEW',
    '2020-05-16 01:00:00',
    '2020-05-16 01:00:00'
)
;
