INSERT INTO crm_admin.campaign
(
    name,
    entity_type,
    trend,
    discount,
    state,
    salt,
    created_at
)
VALUES
(
    'name',
    'User',
    'user_trend',
    True,
    'NEW',
    'salt',
    '2021-03-12 01:00:00'
),
(
    'name',
    'EatsUser',
    'eats_trend',
    True,
    'NEW',
    'salt',
    '2021-03-12 01:00:00'
),
(
    'name',
    'Driver',
    'driver_trend',
    True,
    'NEW',
    'other salt',
    '2021-03-12 01:00:00'
),
(
    'name',
    'EatsUser',
    'not_eats_trend',
    True,
    'NEW',
    'salt',
    '2021-03-12 01:00:00'
);
