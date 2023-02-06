INSERT INTO crm_admin.campaign
(id, name, entity_type, trend, discount, state, created_at)
VALUES
(1, 'campaign_1', 'entity_type', 'trend', FALSE, 'SEGMENT_CALCULATING', '2020-11-13 15:00:00'),
(2, 'campaign_2', 'entity_type', 'trend', FALSE, 'SEGMENT_CALCULATING', '2020-11-13 15:00:00'),
(3, 'campaign_3', 'entity_type', 'trend', FALSE, 'SEGMENT_CALCULATING', '2020-11-13 15:00:00'),
(4, 'campaign_4', 'entity_type', 'trend', FALSE, 'SEGMENT_CALCULATING', '2020-11-13 15:00:00'),
(5, 'campaign_5', 'entity_type', 'trend', FALSE, 'SEGMENT_CALCULATING', '2020-11-13 15:00:00'),
(6, 'campaign_5', 'entity_type', 'trend', FALSE, 'OTHER_STATE', '2020-11-13 15:00:00'),
(7, 'campaign_5', 'entity_type', 'trend', FALSE, 'SEGMENT_CALCULATING', '2020-11-13 15:00:00')
;

INSERT INTO crm_admin.operations
(id, campaign_id, operation_name, submission_id, operation_type, status, extra_data, started_at, finished_at)
VALUES
(1, 1, 'create_segment',             'submission_id_1', 'spark', 'COMPLETED', '{}'::jsonb, '2020-11-13 15:00:01', '2020-11-13 15:00:00'),
(2, 1, 'create_segment',             'submission_id_2', 'spark', 'PROCESS', '{}'::jsonb, '2020-11-13 15:00:02', NULL),
(3, 1, 'compute_segment_statistics', 'submission_id_2', 'spark', '', '{}'::jsonb, '2020-11-13 15:00:03', NULL),
(4, 1, 'create_segment',             'submission_id_3', 'spark', 'FINISHED', '{}'::jsonb, '2020-11-13 15:00:04', '2020-11-13 15:00:00'),
(5, 1, 'create_segment',             'submission_id_3', 'spark', 'PROCESS', '{}'::jsonb, '2020-11-13 15:00:05', NULL),

(6, 3, 'compute_segment_statistics', 'submission_id_4', 'spark', 'COMPLETED', '{}'::jsonb, '2020-11-13 15:00:00', '2020-11-13 15:00:00'),

(7, 4, 'create_segment',             'submission_id_1', 'yql', 'COMPLETED', '{}'::jsonb, '2020-11-13 15:00:01', '2020-11-13 15:00:00'),
(8, 4, 'create_segment',            'submission_id_3', 'yql', '', '{}'::jsonb, '2020-11-13 15:00:02', '2020-11-13 15:00:00'),
(9, 4, 'compute_segment_statistics', 'submission_id_2', 'yql', 'PROCESS', '{}'::jsonb, '2020-11-13 15:00:03', NULL),
(10, 4, 'create_segment',            'submission_id_3', 'yql', 'FINISHED', '{}'::jsonb, '2020-11-13 15:00:04', '2020-11-13 15:00:00'),
(11, 4, 'create_segment',             'submission_id_2', 'yql', 'PROCESS', '{}'::jsonb, '2020-11-13 15:00:05', NULL),

(12, 5, 'create_segment',            'submission_id_2', 'bad', 'PROCESS', '{}'::jsonb, '2020-11-13 15:00:00', '2020-11-13 15:00:00'),

(13, 7, 'create_segment',            NULL , '', '', '{}'::jsonb, '2020-11-13 15:00:00', NULL),

(14, 6, 'create_segment',            NULL , '', '', '{}'::jsonb, '2020-11-13 15:00:00', NULL)
;
