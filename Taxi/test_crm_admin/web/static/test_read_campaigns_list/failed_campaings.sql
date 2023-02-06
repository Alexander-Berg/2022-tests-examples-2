INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    ticket,
    ticket_status,
    created_at,
    updated_at
)
VALUES
(
    100,
    'name',
    'User',
    'trend',
    'kind',
    True,
    'SEGMENT_ERROR',
    'user',
    'ticket',
    'open',
    '2020-09-16 01:00:00',
    '2020-09-16 01:00:00'
),
(
    101,
    'name',
    'Driver',
    'trend',
    'kind',
    True,
    'GROUPS_ERROR',
    'user',
    'ticket',
    'open',
    '2020-09-16 01:00:00',
    '2020-09-16 01:00:00'
);
