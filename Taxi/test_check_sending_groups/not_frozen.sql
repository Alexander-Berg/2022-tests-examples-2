INSERT INTO crm_admin.segment
(id, yql_shared_url, yt_table, control, created_at)
VALUES
(1, 'yql_shared_url', 'yt_table', 0, '2022-12-12T00:00:00+03:00'),
(2, 'yql_shared_url', 'yt_table', 0, '2022-12-12T00:00:00+03:00'),
(3, 'yql_shared_url', 'yt_table', 0, '2022-12-12T00:00:00+03:00'),
(4, 'yql_shared_url', 'yt_table', 0, '2022-12-12T00:00:00+03:00')
;

INSERT INTO crm_admin.campaign
(id, segment_id, state, updated_at, name, entity_type, trend, discount, created_at)
VALUES
(1, 1, 'NEW', '2022-12-24T13:33:00+03:00', 'name', 'user', 'trend', false, '2022-12-12T00:00:00+03:00'),
(2, 2, 'NEW', '2022-12-12T13:33:00+03:00', 'name', 'user', 'trend', false, '2022-12-12T00:00:00+03:00'),
(3, 3, 'NEW', '2022-12-12T13:33:00+03:00', 'name', 'user', 'trend', false, '2022-12-12T00:00:00+03:00'),
(4, 4, 'NEW', '2022-12-12T13:33:00+03:00', 'name', 'user', 'trend', false, '2022-12-12T00:00:00+03:00')
;

INSERT INTO crm_admin.group_v2
(id, segment_id, name, type, params, updated_at, sending_stats, created_at)
VALUES
(1, 1, 'test', 'FILTER', '{}', '2022-12-12T13:33:00+03:00', NULL,                          '2022-12-12T00:00:00+03:00'),
(2, 2, 'test', 'FILTER', '{}', '2022-12-12T12:20:00+03:00', '{}'::jsonb,                   '2022-12-12T00:00:00+03:00'),
(3, 1, 'test', 'FILTER', '{}', '2022-12-12T13:33:00+03:00', NULL,                          '2022-12-12T00:00:00+03:00'),
(4, 2, 'test', 'FILTER', '{}', '2022-12-12T12:20:00+03:00', '{}'::jsonb,                   '2022-12-12T00:00:00+03:00'),
(5, 1, 'test', 'FILTER', '{}', '2022-12-12T13:33:00+03:00', NULL,                          '2022-12-12T00:00:00+03:00'),
(6, 2, 'test', 'FILTER', '{}', '2022-12-12T13:33:00+03:00', NULL,                          '2022-12-12T00:00:00+03:00'),
(7, 3, 'test', 'FILTER', '{}', '2022-12-12T12:20:00+03:00', '{"planned": 100}'::jsonb,     '2022-12-12T00:00:00+03:00'),
(8, 3, 'test', 'FILTER', '{}', '2022-12-12T12:20:00+03:00', '{"planned": 100}'::jsonb,     '2022-12-12T00:00:00+03:00')
;

TRUNCATE TABLE crm_admin.group_state_log_v2;

INSERT INTO crm_admin.group_state_log_v2
(group_id, state_from, state_to, updated_at)
VALUES
-- correct time and sending stats is null, NOT FROZEN
(3, '',                     'SENDING',  '2022-12-12T11:55:00'),
-- correct time and sending stats is {}, NOT FROZEN
(4, '',                     'SENDING',  '2022-12-12T11:50:00'),

-- correct time and sending stats is null, NOT FROZEN
(5, 'SCHEDULED',            'SENDING',  '2022-12-12T11:50:00'),
(5, 'SENDING',              'SENT',     '2022-12-12T12:00:00'),

-- correct time and sending stats is not null, NOT FROZEN
(7, 'SCHEDULED',            'SENDING',  '2022-12-12T11:50:00'),
(7, 'SENDING',              'SENT',     '2022-12-12T12:00:00'),
-- incorrect time and sending stats is not null, NOT FROZEN
(8, 'SCHEDULED',            'SENDING',  '2022-12-12T11:49:59'),
(8, 'SENDING',              'SENT',     '2022-12-12T12:00:00')
;
