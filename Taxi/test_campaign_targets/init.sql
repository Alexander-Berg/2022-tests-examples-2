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
),
(
    3,
    'campaign #3',
    'User',
    'trend',
    'kind',
    True,
    'READY',
    'ticket',
    '2020-10-26 01:00:00'
);


INSERT INTO crm_admin.target
(
 id,
 owner,
 name,
 label,
 const_salt,
 created_at,
 updated_at
)
VALUES
(
    1,
    'leemurus',
    'target',
    'target_1',
    'asdx21c423c4234c234',
    '2022-02-24 04:00:00',
    '2022-02-24 04:00:00'
),
(
    2,
    'leemurus',
    'target',
    'target_2',
    'asdx21c423c4234c234',
    '2022-02-24 04:00:00',
    '2022-02-24 04:00:00'
),
(
    4,
    'leemurus',
    'target',
    'target_3',
    'asdx21c423c4234c234',
    '2022-02-24 04:00:00',
    '2022-02-24 04:00:00'
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
),
(
    4,
    3,
    4,
    '2022-02-24 04:00:00',
    '2022-02-24 04:00:00',
    '2022-02-24 04:00:04'
);


SELECT setval(
    'crm_admin.campaign_target_connection_id_seq',
    (
        SELECT MAX(id)
        FROM crm_admin.campaign_target_connection
    )
);
