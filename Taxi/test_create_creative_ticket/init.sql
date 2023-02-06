INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    discount,
    state,
    owner_name,
    ticket,
    creative,
    created_at
)
VALUES
(
    1,
    'user campaign',
    'User',
    'trend',
    True,
    'NEW',
    'username',
    'ticket-1',
    null,
    '2020-08-07 01:00:00'
),
(
    2,
    'driver campaign',
    'Driver',
    'trend',
    True,
    'NEW',
    'username',
    'ticket-2',
    null,
    '2020-08-07 01:00:00'
),
(
    3,
    'driver campaign with a creative ticket',
    'Driver',
    'trend',
    True,
    'NEW',
    'username',
    'ticket-3',
    'creative-ticker-1',
    '2020-08-07 01:00:00'
);
