INSERT INTO crm_admin.campaign
(
    name,
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
    planned_start_date,
    settings
)
VALUES
(
    'campaing #1',
    'Driver',
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
    CURRENT_DATE,
    ('[{"value": "taximeter", "fieldId": "app"}]')::jsonb
);
