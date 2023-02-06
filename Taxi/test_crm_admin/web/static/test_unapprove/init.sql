INSERT INTO crm_admin.campaign
(
    id, name,       entity_type, trend, kind, subkind,
    discount, state, owner_name, ticket, ticket_status, settings,
    created_at, updated_at, is_regular, is_active,
    efficiency_start_time, efficiency_stop_time
) VALUES (
    1, 'Trend only', 'User',     '',  null, null,
    false, 'PENDING', 'owner_1', 'CRMTEST-1', 'Open', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    2, 'Trend only', 'User',     'without_approvers',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Open', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
)
;
