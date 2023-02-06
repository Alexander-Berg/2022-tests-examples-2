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
    'segment1_yql_shred_link',
    'segment1_yt_table',
    ('{}')::jsonb,
    'Share',
    20,
    '2019-11-20 01:00:00'
);

INSERT INTO crm_admin.campaign
(name, segment_id, entity_type, trend, discount, state, global_control, com_politic, created_at)
VALUES(
    'campaign',
    1,
    'Driver',
    'trend',
    false,
    'READY',
    false,
    false,
    '2021-03-12 01:00:00'
)
;
