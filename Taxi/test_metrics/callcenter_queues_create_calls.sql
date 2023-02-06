INSERT INTO callcenter_queues.calls
    (asterisk_call_id,
     routing_id  ,
     metaqueue   ,
     subcluster ,
     status ,
     last_event_at  ,
     call_guid ,
     called_number,
     abonent_phone_id ,
     queued_at,
     answered_at,
     completed_at ,
     endreason ,
     transfered_to_number ,
     asterisk_agent_id)
VALUES
    -- for statistics of active calls
    ('10', '10', 'queue', '1', 'queued', '2020-06-22T10:00:05.00Z', null, null, null, '2020-06-22T10:00:00.00Z', null, null, null, null, null),
    ('11', '11', 'queue', '1', 'queued', '2020-06-22T10:00:05.00Z', null, null, null, '2020-06-22T10:00:01.00Z', null, null, null, null, null),
    ('13', '13', 'queue', '2', 'queued', '2020-06-22T10:00:05.00Z', null, null, null, '2020-06-22T10:00:03.50Z', null, null, null, null, null),
    ('14', '14', 'queue', '2', 'talking', '2020-06-22T10:00:05.00Z', null, null, null, '2020-06-22T10:00:04.00Z', '2020-06-22T10:00:05.00Z', null, null, null, null),
    ('15', '15', 'queue', '2', 'talking', '2020-06-22T10:00:05.00Z', null, null, null, '2020-06-22T10:00:05.00Z', '2020-06-22T10:00:07.00Z', null, null, null, null),
    ('16', '16', 'queue', '3', 'talking', '2020-06-22T10:00:05.00Z', null, null, null, '2020-06-22T10:00:05.00Z', '2020-06-22T10:00:07.00Z', null, null, null, null),
    -- for statistics of last completed calls
    ('21', '21', 'queue', '2', 'completed',  '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL, '2020-06-22T08:00:00.00Z', null, '2020-06-22T09:00:00.00Z','completed_by_caller', '2020-06-22T09:00:00.00Z', NULL), -- out of statistics of last minute
    ('22', '22', 'queue', '2', 'completed', '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL, '2020-06-22T09:59:50.00Z', '2020-06-22T09:59:59.00Z', '2020-06-22T10:00:00.00Z','completed_by_caller', '2020-06-22T10:00:00.00Z', NULL),
    ('23', '23', 'queue', '2', 'completed',  '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL,'2020-06-22T09:59:50.00Z', '2020-06-22T09:59:56.00Z', '2020-06-22T10:00:00.00Z','completed_by_agent', '2020-06-22T10:00:00.00Z', NULL),
    ('24', '24', 'queue', '2', 'completed', '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL, '2020-06-22T09:59:50.00Z', '2020-06-22T09:59:59.00Z', '2020-06-22T10:00:00.00Z','completed_by_agent', '2020-06-22T10:00:00.00Z', NULL),
    ('25', '25', 'queue', '2', 'completed',  '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL,'2020-06-22T09:59:50.00Z', null, '2020-06-22T10:00:00.00Z','abandoned', '2020-06-22T10:00:00.00Z', NULL),
    ('26', '26', 'queue', '2', 'completed', '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL, '2020-06-22T09:59:50.00Z', null, '2020-06-22T10:00:00.00Z','abandoned', '2020-06-22T10:00:00.00Z', NULL),
    ('27', '27', 'queue', '2', 'completed',  '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL,'2020-06-22T09:59:50.00Z', null, '2020-06-22T10:00:00.00Z','abandoned', '2020-06-22T10:00:00.00Z', NULL),
    ('28', '28', 'queue', '2', 'completed', '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL, '2020-06-22T09:59:50.00Z', '2020-06-22T09:59:50.00Z', '2020-06-22T10:00:00.00Z','transfered', '2020-06-22T10:00:00.00Z', NULL),
    ('29', '29', 'queue', '2', 'completed',  '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL,'2020-06-22T09:59:50.00Z', '2020-06-22T09:59:50.00Z', '2020-06-22T10:00:00.00Z','transfered', '2020-06-22T10:00:00.00Z', NULL),
    ('30', '30', 'queue', '2', 'completed', '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL, '2020-06-22T09:59:50.00Z', '2020-06-22T09:59:50.00Z', '2020-06-22T10:00:00.00Z','transfered', '2020-06-22T10:00:00.00Z', NULL),
    ('31', '31', 'queue', '2', 'completed',  '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL,'2020-06-22T09:59:50.00Z', '2020-06-22T09:59:50.00Z', '2020-06-22T10:00:00.00Z','transfered', '2020-06-22T10:00:00.00Z', NULL),
    ('32', '32', 'queue', '2', 'completed', '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL, '2020-06-22T09:59:50.00Z', '2020-06-22T09:59:50.00Z', '2020-06-22T10:00:00.00Z','transfered', '2020-06-22T10:00:00.00Z', NULL),
    ('33', '33', 'queue', '2', 'completed',  '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL,'2020-06-22T09:59:50.00Z', '2020-06-22T09:59:50.00Z', '2020-06-22T10:00:00.00Z','transfered', '2020-06-22T10:00:00.00Z', NULL),
    ('34', '34', 'queue', '2', 'completed', '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL, '2020-06-22T09:59:50.00Z', '2020-06-22T09:59:50.00Z', '2020-06-22T10:00:00.00Z','transfered', '2020-06-22T10:00:00.00Z', NULL),
    ('35', '35', 'queue', '2', 'completed',  '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL,'2020-06-22T09:59:50.00Z', '2020-06-22T09:59:50.00Z', '2020-06-22T10:00:00.00Z','transfered', '2020-06-22T10:00:00.00Z', NULL),
    ('36', '36', 'queue', '2', 'completed', '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL, '2020-06-22T09:59:50.00Z', '2020-06-22T09:59:59.00Z', '2020-06-22T10:00:00.00Z','transfered', '2020-06-22T10:00:00.00Z', NULL),
    ('37', '37', 'queue', '1', 'completed',  '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL,'2020-06-22T09:59:59.00Z', '2020-06-22T10:00:00.00Z', '2020-06-22T10:00:00.00Z','completed_by_caller', '2020-06-22T10:00:00.00Z', NULL),
    ('38', '38', 'queue', '1', 'completed', '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL, '2020-06-22T09:59:51.00Z', '2020-06-22T10:00:00.00Z', '2020-06-22T10:00:00.00Z','completed_by_agent', '2020-06-22T10:00:00.00Z', NULL),
    ('39', '39', 'queue', '1', 'completed',  '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL,'2020-06-22T09:59:51.00Z', null, '2020-06-22T09:59:53.00Z','abandoned', '2020-06-22T09:59:53.00Z', NULL),
    ('40', '40', 'queue', '1', 'completed', '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL, '2020-06-22T09:59:51.00Z', '2020-06-22T10:00:00.00Z', '2020-06-22T10:00:00.00Z','transfered', '2020-06-22T10:00:00.00Z', NULL),
    ('41', '41', 'queue', '3', 'completed',  '2020-06-22T10:00:00.00Z',  NULL, NULL, NULL,'2020-06-22T09:59:51.50Z', '2020-06-22T09:59:54.50Z', '2020-06-22T10:00:00.00Z','completed_by_caller', '2020-06-22T10:00:00.00Z', NULL)