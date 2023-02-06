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
    '//home/clear_node/table1',
    'Share',
    20,
    '2021-03-27 01:00:00'
),
(
    2,  -- id
    'yql_shared_url',
    '//home/clear_node/table2',
    'Share',
    20,
    '2021-03-27 01:00:00'
),
(
    3,  -- id
    'yql_shared_url',
    '//home/clear_node/table3',
    'Share',
    20,
    '2021-03-27 01:00:00'
);


INSERT INTO crm_admin.campaign
(
    segment_id,
    name,
    entity_type,
    trend,
    state,
    is_regular,
    is_active,
    created_at,
    updated_at,
    discount
)
VALUES
(
    -- id: 1
    1,  -- segment_id
    'oneshot campaign',
    'User',
    'trend',
    'CANCELED',
    False,  -- is_regular
    False,  -- is_active
    '2021-03-01 01:00:00',
    '2021-04-01 01:00:00',
    True
),
(
    -- id: 2
    2,  -- segment_id
    'regular campaign',
    'Driver',
    'trend',
    'SCHEDULED',
    True,  -- is_regular
    True,  -- is_active
    '2021-03-01 01:00:00',
    '2021-04-01 01:00:00',
    True
),
(
    -- id: 3
    3,  -- segment_id
    'oneshot campaign',
    'Driver',
    'trend',
    'CANCELED',
    False,  -- is_regular
    False,  -- is_active
    '2021-05-15 01:00:00',
    '2021-05-15 01:00:00',
    True
);


TRUNCATE crm_admin.campaign_state_log;

INSERT INTO crm_admin.campaign_state_log
    (campaign_id, state_from, state_to, updated_at)
SELECT id, '', 'NEW', created_at + '3 hours' FROM crm_admin.campaign;

INSERT INTO crm_admin.campaign_state_log
    (campaign_id, state_from, state_to, updated_at)
SELECT id, 'NEW', state, updated_at + '3 hours' FROM crm_admin.campaign;

-- simulate missing log
DELETE FROM crm_admin.campaign_state_log
WHERE campaign_id IN (1);
