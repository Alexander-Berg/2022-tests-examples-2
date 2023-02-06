INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    discount,
    state,
    is_regular,
    is_active,
    salt,
    created_at,
    root_id,
    parent_id,
    child_id,
    version_state
)
VALUES
(
    1,
    'name',
    'User',
    'trend',
    True,
    'SCHEDULED',
    true,
    true,
    'salt',
    '2021-03-12 01:00:00',
    1,
    null,
    2,
    'ACTUAL'
),
(
    2,
    'name',
    'User',
    'trend',
    True,
    'APPLYING_DRAFT',
    true,
    true,
    'salt',
    '2021-03-12 01:00:00',
    1,
    1,
    null,
    'DRAFT'
),
(
    3,
    'name',
    'User',
    'trend',
    True,
    'SCHEDULED',
    true,
    true,
    'salt',
    '2021-03-12 01:00:00',
    3,
    null,
    4,
    'ACTUAL'
),
(
    4,
    'name',
    'User',
    'trend',
    True,
    'APPLYING_DRAFT',
    true,
    true,
    'salt',
    '2021-03-12 01:00:00',
    3,
    3,
    null,
    'DRAFT'
),
(
    5,
    'name',
    'User',
    'trend',
    True,
    'SCHEDULED',
    true,
    true,
    'salt',
    '2021-03-12 01:00:00',
    5,
    null,
    6,
    'ACTUAL'
),
(
    6,
    'name',
    'User',
    'trend',
    True,
    'GROUPS_FINISHED',
    true,
    true,
    'salt',
    '2021-03-12 01:00:00',
    5,
    5,
    null,
    'DRAFT'
);

INSERT INTO crm_admin.draft_applying
(
    draft_campaign_id,
    created_at,
    updated_at
)
VALUES
(
    2,
    '2021-03-12 01:00:00',
    '2021-03-12 01:00:00'
),
(
    6,
    '2021-03-12 01:00:00',
    '2021-03-12 01:00:00'
);
