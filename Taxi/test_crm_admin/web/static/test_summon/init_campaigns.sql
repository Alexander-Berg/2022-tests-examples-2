INSERT INTO crm_admin.campaign
(
    id, name,       entity_type, trend, kind, subkind,
    discount, state, owner_name, ticket, ticket_status, settings,
    created_at, updated_at, is_regular, is_active,
    efficiency_start_time, efficiency_stop_time
) VALUES (
    -- without trend
    1, 'Trend only', 'User',     '',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- without approvers
    2, 'Trend only', 'User',     'without_approvers',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- trend only
    3, 'Trend only', 'User',     'Trend_1',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- drivers by kind
    4, 'By kind', 'Driver',     'Trend_1',  'the_kind', null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- drivers by defaults
    5, 'By defaults', 'Driver',     'Trend_1',  'other_kind', null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- drivers no analyst
    6, 'By defaults', 'Driver',     'Trend_1',  'other_kind', null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[{"value": ["br_israel"], "fieldId": "country"}]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- users regular not active
    7, 'Trend only', 'User',     'Trend_1',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', TRUE, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- users regular not active
    8, 'Trend only', 'User',     'Trend_1',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', TRUE, TRUE,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- trend only EatsUser
    9, 'Trend only', 'EatsUser',     'Trend_1',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- without approvers EatsUser
    10, 'Trend only', 'EatsUser',     'without_approvers',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- without trend EatsUser
    11, 'Trend only', 'EatsUser',     '',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- with kind User
    12, 'Trend only', 'User',     'Trend_2',  'Kind_2', null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- with subkind User
    13, 'Trend only', 'User',     'Trend_2',  'Kind_2', 'Subkind_2',
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- with kind User
    22, 'Trend only', 'LavkaUser',     'Trend_2',  'Kind_2', null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
),
(
    -- with subkind User
    23, 'Trend only', 'LavkaUser',     'Trend_2',  'Kind_2', 'Subkind_2',
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null,
    '2020-01-20 01:00:00', '2020-12-20 01:00:00'
);


INSERT INTO crm_admin.campaign
(
    id, name,       entity_type, trend, kind, subkind,
    discount, state, owner_name, ticket, ticket_status, settings,
    created_at, updated_at, is_regular, is_active
) VALUES (
    -- trend only LavkaUser
    14, 'Trend only', 'LavkaUser',     'Trend_1',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[{"value": ["br_russia"], "fieldId": "country"}]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null
),
(
    -- without approvers LavkaUser
    15, 'Trend only', 'LavkaUser',     'without_approvers',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[{"value": ["br_russia"], "fieldId": "country"}]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null
),
(
    -- with kind LavkaUser
    16, 'Trend only', 'LavkaUser',     'Trend_2',  'Kind_2', null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null
),
(
    -- with subkind LavkaUser
    17, 'Trend only', 'LavkaUser',     'Trend_2',  'Kind_2', 'Subkind_2',
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null
),
(
    -- trend only LavkaUser deli-israel
    18, 'Trend only', 'LavkaUser',     'Trend_1',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[{"value": ["br_israel"], "fieldId": "country"}]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null
),
(
    -- trend only LavkaUser deli-israel & common
    19, 'Trend only', 'LavkaUser',     'Trend_1',  null, null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[{"value": ["br_israel"], "fieldId": "country"}, {"value": ["br_russia"], "fieldId": "country"}]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null
),
(
    -- with kind LavkaUser #2
    20, 'Trend only', 'LavkaUser',     'Trend_1',  'Kind_3', null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[{"value": ["br_russia"], "fieldId": "country"}]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null
),
(
    -- with kind User #2
    21, 'Trend only', 'User',     'Trend_1',  'Kind_3', null,
    false, 'VERIFY_FINISHED', 'owner_1', 'CRMTEST-1', 'Открыт', '[{"value": ["br_russia"], "fieldId": "country"}]',
    '2020-03-20 01:00:00', '2020-03-20 01:00:00', null, null
);
