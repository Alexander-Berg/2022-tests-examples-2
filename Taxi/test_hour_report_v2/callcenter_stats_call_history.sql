INSERT INTO callcenter_stats.call_history
(id, call_id, queue, queued_at, answered_at, completed_at, created_at, endreason, direction)
VALUES
    -- for statistics of last completed calls
    ('21', '21', 'disp_on_1', '2020-06-23T08:00:00.00Z', null, '2020-06-23T08:50:00.00Z', '2020-06-23T08:50:00.00Z', 'completed_by_caller', 'in'), -- out of statistics of last minute
    ('22', '22', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:59.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'completed_by_caller', 'in'),
    ('23', '23', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:56.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'completed_by_agent', 'in'),
    ('24', '24', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:59.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'completed_by_agent', 'in'),
    ('25', '25', 'disp_on_1', '2020-06-23T09:49:50.00Z', null, '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'abandoned', 'in'),
    ('26', '26', 'disp_on_1', '2020-06-23T09:49:50.00Z', null, '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'abandoned', 'in'),
    ('27', '27', 'disp_on_1', '2020-06-23T09:49:50.00Z', null, '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'abandoned', 'in'),
    ('28', '28', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:50.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'transfered', 'in'),
    ('29', '29', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:50.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'transfered', 'in'),
    ('30', '30', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:50.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'transfered', 'in'),
    ('31', '31', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:50.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'transfered', 'in'),
    ('32', '32', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:50.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'transfered', 'in'),
    ('33', '33', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:50.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'transfered', 'in'),
    ('34', '34', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:50.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'transfered', null),
    ('35', '35', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:50.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'transfered', null),
    ('36', '36', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:59.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'transfered', 'in'),
    ('37', '37', 'support_on_1', '2020-06-23T09:49:59.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'completed_by_caller', 'in'),
    ('38', '38', 'support_on_1', '2020-06-23T09:49:51.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'completed_by_agent', 'in'),
    ('39', '39', 'support_on_1', '2020-06-23T09:49:51.00Z', null, '2020-06-23T09:49:53.00Z', '2020-06-23T09:49:53.00Z', 'abandoned', 'in'),
    ('40', '40', 'support_on_1', '2020-06-23T09:49:51.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'transfered', null),
    ('41', '41', 'disp_on_1', '2020-06-23T09:49:50.00Z', '2020-06-23T09:49:59.00Z', '2020-06-23T09:50:00.00Z', '2020-06-23T09:50:00.00Z', 'transfered', 'out')