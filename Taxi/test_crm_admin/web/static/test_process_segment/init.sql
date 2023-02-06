INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    discount,
    state,
    creative,
    is_regular,
    is_active,
    created_at
)
VALUES
(
    1,  -- id
    'User campaign',
    'User',
    'trend',
    True,
    'READY',
    'creative',
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00'
),
(
    2,  -- id
    'Driver campaign',
    'User',
    'trend',
    True,
    'READY',
    null,  -- creative
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00'
),
(
    3,  -- id
    'EatsUser campaign',
    'EatsUser',
    'trend',
    True,
    'READY',
    null,  -- creative
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00'
),
(
    4,  -- id
    'invalid state',
    'User',
    'trend',
    True,
    'NEW',
    'creative',
    False,  -- is_regular
    False,  -- is_active
    '2021-02-03 01:00:00'
);
