insert into crm_admin.segment
(id, yql_shared_url, yt_table, control, created_at)
values
(1, 'yql_shared_url', 'yt_table', 0.00, '2021-01-19T10:00:00+03:00'),
(2, 'yql_shared_url', 'yt_table', 0.00, '2021-01-19T10:00:00+03:00')
;

insert into crm_admin.group
(id, segment_id, sending_stats, params, created_at, updated_at)
values
(
    1,
    1,
    NULL,
    '{"name": "gr1", "limit": 0, "cities": [], "locales": []}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
),
(
    2,
    1,
    '{}',
    '{"name": "gr2", "limit": 0, "cities": [], "locales": []}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
),
(
    3,
    1,
    '{"sent": 167, "failed": 633, "planned": 1000, "skipped": 200, "denied": 0, "finished_at": "2021-01-19T10:00:00+03:00"}',
    '{"channel": "SMS", "state": "EFFICIENCY_ANALYSIS", "name": "gr3", "limit": 0, "cities": [], "locales": [], "computed": {"PUSH": 9993, "total": 10000, "promo.fs": 8388}}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
),
(
    4,
    1,
    '{"sent": 167, "failed": 633, "planned": 1000, "skipped": 200, "denied": 0, "finished_at": "2021-01-19T10:00:00+03:00"}',
    '{"channel": "PUSH", "state": "EFFICIENCY_ANALYSIS", "name": "gr3", "limit": 0, "cities": [], "locales": [], "computed": {"PUSH": 9993, "total": 10000, "promo.fs": 8388}}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
),
(
    5,
    1,
    '{"sent": 167, "failed": 633, "planned": 1000, "skipped": 200, "denied": 0, "finished_at": "2021-01-19T10:00:00+03:00"}',
    '{"channel": "promo.fs", "state": "EFFICIENCY_ANALYSIS", "name": "gr3", "limit": 0, "cities": [], "locales": [], "computed": {"PUSH": 9993, "total": 10000, "promo.fs": 8388}}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
),
(
    6,
    1,
    '{"sent": 167, "failed": 633, "planned": 1000, "skipped": 200, "denied": 9000, "finished_at": "2021-01-19T10:00:00+03:00"}',
    '{"channel": "SMS", "state": "EFFICIENCY_DENIED", "name": "gr3", "limit": 0, "cities": [], "locales": [], "computed": {"PUSH": 9993, "total": 10000, "promo.fs": 8388}}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
),
(
    7,
    1,
    '{"sent": 167, "failed": 633, "planned": 1000, "skipped": 200, "denied": 8993, "finished_at": "2021-01-19T10:00:00+03:00"}',
    '{"channel": "PUSH", "state": "EFFICIENCY_DENIED", "name": "gr3", "limit": 0, "cities": [], "locales": [], "computed": {"PUSH": 9993, "total": 10000, "promo.fs": 8388}}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
),
(
    8,
    1,
    '{"sent": 167, "failed": 633, "planned": 1000, "skipped": 200, "denied": 7388, "finished_at": "2021-01-19T10:00:00+03:00"}',
    '{"channel": "promo.fs", "state": "EFFICIENCY_DENIED", "name": "gr3", "limit": 0, "cities": [], "locales": [], "computed": {"PUSH": 9993, "total": 10000, "promo.fs": 8388}}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
),
(
    9,
    1,
    '{}',
    '{"state": "NEW", "name": "gr3", "limit": 0, "cities": [], "locales": [], "computed": {"PUSH": 9993, "total": 10000, "promo.fs": 8388}}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
);

insert into crm_admin.campaign
(id, segment_id, name, entity_type, trend, discount, state, owner_name, created_at, efficiency)
values
(1, 1, 'name', 'user', 'trend', false, 'SENDING_PROCESSING', 'stasnam', '2021-01-19T10:00:00+03:00', true),
(2, 2, 'name', 'user', 'trend', false, 'SENDING_PROCESSING', 'stasnam', '2021-01-19T10:00:00+03:00', false)
;
