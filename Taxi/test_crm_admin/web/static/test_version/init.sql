INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    discount,
    state,
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
    'NEW',
    'salt',
    '2021-03-12 01:00:00',
    1,
    null,
    2,
    'ARCHIVE'
),
(
    2,
    'name',
    'User',
    'trend',
    True,
    'NEW',
    'salt',
    '2021-03-12 01:00:00',
    1,
    1,
    3,
    'ACTUAL'
),
(
    3,
    'name',
    'User',
    'trend',
    True,
    'NEW',
    'other salt',
    '2021-03-12 01:00:00',
    1,
    2,
    null,
    'DRAFT'
),
(
    4,
    'name',
    'User',
    'trend',
    True,
    'NEW',
    'other salt',
    '2021-03-12 01:00:00',
    null,
    null,
    null,
    'ACTUAL'
);

INSERT INTO crm_admin.draft_applying
(
    actual_campaign_id,
    draft_campaign_id,
    is_applied,
    created_at,
    updated_at
)
VALUES
(
    null,
    1,
    true,
    '2021-03-12 01:00:00',
    '2021-03-12 02:00:00'
),
(
    1,
    2,
    true,
    '2021-03-12 03:00:00',
    '2021-03-12 04:00:00'
),
(
    null,
    4,
    true,
    '2021-03-12 05:00:00',
    '2021-03-12 06:00:00'
)
;
