INSERT INTO crm_admin.target
(
    id,
    owner,
    name,
    label,
    is_available,
    is_important,
    const_salt,
    created_at,
    updated_at
)
VALUES
(
    1,
    'owner',
    'name',
    'label_1',
    true,
    true,
    'const_salt_1',
    '2020-10-26 01:00:00',
    '2020-10-26 01:00:00'
),
(
    2,
    'owner',
    'name',
    'label_2',
    true,
    true,
    'const_salt_2',
    '2020-10-26 01:00:00',
    '2020-10-26 01:00:00'
),
(
    3,
    'owner',
    'name',
    'label_3',
    true,
    true,
    'const_salt_3',
    '2020-10-26 01:00:00',
    '2020-10-26 01:00:00'
),
(
    4,
    'owner',
    'name',
    'label_4',
    true,
    true,
    'const_salt_4',
    '2020-10-26 01:00:00',
    '2020-10-26 01:00:00'
),
(
    5,
    'owner',
    'name',
    'label_5',
    true,
    false,
    'const_salt_5',
    '2020-10-26 01:00:00',
    '2020-10-26 01:00:00'
),
(
    6,
    'owner',
    'name',
    'label_6',
    true,
    true,
    'const_salt_6',
    '2020-10-26 01:00:00',
    '2020-10-26 01:00:00'
);

INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    kind,
    discount,
    state,
    ticket,
    created_at
)
VALUES
(
    1,
    'campaign #1',
    'User',
    'trend',
    'kind',
    True,
    'READY',
    'ticket',
    '2020-10-26 01:00:00'
);

INSERT INTO crm_admin.campaign_target_connection
(
    id,
    campaign_id,
    target_id,
    created_at,
    updated_at,
    deleted_at
)
VALUES
(
    1,
    1,
    1,
    '2022-02-24 04:00:00',
    '2022-02-24 04:00:00',
    NULL
),
(
    2,
    1,
    2,
    '2022-02-24 04:00:00',
    '2022-02-24 04:00:00',
    NULL
);


SELECT setval(
    'crm_admin.campaign_target_connection_id_seq',
    (
        SELECT MAX(id)
        FROM crm_admin.campaign_target_connection
    )
);
