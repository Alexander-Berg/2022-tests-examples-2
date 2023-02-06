INSERT INTO crm_admin.segment
(id, yql_shared_url, yt_table, control, created_at)
VALUES
(1, 'yql_shared_url', 'yt_table', 0, '2022-12-22T00:00:00+03:00'),
(2, 'yql_shared_url', 'yt_table', 0, '2022-12-22T00:00:00+03:00'),
(3, 'yql_shared_url', 'yt_table', 0, '2022-12-22T00:00:00+03:00'),
(4, 'yql_shared_url', 'yt_table', 0, '2022-12-22T00:00:00+03:00'),
(5, 'yql_shared_url', 'yt_table', 0, '2022-12-22T00:00:00+03:00')
;

INSERT INTO crm_admin.campaign
(id, segment_id, state, updated_at, name, entity_type, trend, discount, created_at)
VALUES
(1, 1, 'EFFICIENCY_ANALYSIS', '2022-12-22T12:00:00+03:00', 'name', 'User', 'trend', false, '2022-12-22T00:00:00+03:00'),
(2, 2, 'EFFICIENCY_ANALYSIS', '2022-12-22T12:00:00+03:00', 'name', 'User', 'trend', false, '2022-12-22T00:00:00+03:00'),
(3, 3, 'FINISHED',            '2022-12-22T12:00:00+03:00', 'name', 'User', 'trend', false, '2022-12-22T00:00:00+03:00'),
(4, 4, 'EFFICIENCY_ANALYSIS', '2022-12-22T12:00:00+03:00', 'name', 'Driver', 'trend', false, '2022-12-22T00:00:00+03:00'),
(5, 5, 'EFFICIENCY_ANALYSIS', '2022-12-22T12:00:00+03:00', 'name', 'Driver', 'trend', false, '2022-12-22T00:00:00+03:00')
;

TRUNCATE TABLE crm_admin.campaign_state_log;

INSERT INTO crm_admin.campaign_state_log
(campaign_id, state_from, state_to, updated_at)
VALUES
-- another campaign status, NOT FROZEN
(3, '', 'EFFICIENCY_ANALYSIS', '2022-12-21T00:00:00'),
-- just not frozen, NOT FROZEN
(4, '', 'EFFICIENCY_ANALYSIS', '2022-12-12T12:00:00'),
-- check hours, NOT FROZEN
(5, '', 'EFFICIENCY_ANALYSIS', '2022-12-05T12:00:00')
;
