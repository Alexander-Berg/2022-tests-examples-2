-- segments --
INSERT INTO crm_admin.segment
(id, yql_shared_url, yt_table, aggregate_info, mode, control, created_at)
VALUES
(9, 'segment6_yql_shred_link', 'segment6_yt_table', ('{}')::jsonb, 'Share', 20, '2019-11-20 01:00:00');


-- groups --
INSERT INTO crm_admin.group
(id, segment_id, prepared_at, created_at, updated_at, params)
VALUES
(12, 9, '2019-11-20 02:00:00', '2019-11-20 01:00:00', '2019-11-20 01:00:00', ('{"name": "UserGroup", "state": "SENDING", "channel": "PUSH", "content": "user_fs_id", "feed_id": "qwe", "share": 10}')::jsonb);

INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    state,
    name,
    entity_type,
    trend,
    kind,
    subkind,
    discount,
    owner_name,
    ticket,
    ticket_status,
    global_control,
    com_politic,
    created_at,
    updated_at
)
VALUES
(
    9,
    9,
    'CAMPAIGN_APPROVED',
    'Кампания 8',
    'User',
    'Направление или тип пользовательской кампании',
    'Тип или подтип пользовательской кампании',
    'subkind',
    True,
    'user1',
    'user_ticket',
    'Открыт',
    True,
    True,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
);
