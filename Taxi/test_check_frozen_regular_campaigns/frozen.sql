INSERT INTO crm_admin.campaign
(id, entity_type, name, created_at, state, discount, trend, is_regular, is_active)
VALUES
(1, '', '', '2022-12-28 10:00:00', 'GROUPS_FINISHED', true, '', true, true),
(2, '', '', '2022-12-28 10:00:00', 'SEGMENT_FINISHED', true, '', true, true),
(3, '', '', '2022-12-28 10:00:00', 'SCHEDULED', true, '', true, true),
(4, '', '', '2022-12-28 10:00:00', 'SCHEDULED', true, '', true, true);

INSERT INTO crm_admin.schedule
(campaign_id, final_state, scheduled_for, started_at, finished_at, sending_stats)
VALUES
(1, '', '2022-12-28 11:00:00', null, null, '{}'),
(2, '', '2022-12-28 11:00:00', null, null, '{}'),
(3, '', '2022-12-28 11:00:00', null, null, '{}'),
(4, '', '2022-12-28 18:00:00', null, null, '{}');


INSERT INTO crm_admin.campaign_state_log
(campaign_id, state_from, state_to, updated_at)
VALUES
(1, '', 'GROUPS_FINISHED', '2022-12-28 14:58:00'),
(1, '', 'SEGMENT_FINISHED', '2022-12-28 14:50:00'),
(2, '', 'GROUPS_FINISHED', '2022-12-28 14:30:00');
