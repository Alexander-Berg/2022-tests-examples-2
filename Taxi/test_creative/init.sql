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
    ('{"channel_name": "driver_sms", "content": "Hello!", "intent": "intent", "sender": "sender"}')::jsonb,
    '2021-01-27 01:00:00',
    '2021-01-27 01:00:00'
);

INSERT INTO crm_admin.campaign
(
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
    is_active,
    test_users,
    com_politic,
    efficiency,
    tasks,
    planned_start_date
)
VALUES
(
    'campaing #1',
    NULL,
    'User',
    'campaign #1 trend',
    'campaign #1 kind',
    True,
    'GROUPS_READY',
    'user1',
    True,
    'ticket #1',
    '2020-04-01 01:00:00',
    True,
    '{}',
    False,
    False,
    '{}',
    CURRENT_DATE
);

INSERT INTO crm_admin.campaign_creative_connection
(
    campaign_id,
    creative_id,
    created_at
) VALUES
(1, 1, NOW());
