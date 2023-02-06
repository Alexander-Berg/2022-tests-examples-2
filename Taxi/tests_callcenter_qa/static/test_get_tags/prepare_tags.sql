INSERT INTO callcenter_qa.tags
(uuid, project, personal_phone_id, reason, blocked_until, extra)
VALUES
    ('id1', 'disp', 'phone_pd_test', 'children', '2020-07-19 11:14:40.00+0000',
     '{"application": "test_app_1", "metaqueue": "test_disp_queue_1"}'),
    ('id2', 'disp', 'phone_pd_test', 'children', '2020-07-19 11:13:40.00+0000',
     '{"application": "test_app_1", "metaqueue": "test_disp_queue_1"}'),
    ('id3', 'disp', 'phone_pd_test', 'children', '2020-07-19 11:14:40.00+0000',
     '{"application": "test_app_2", "metaqueue": "test_disp_queue_1"}'),
    ('id4', 'help', 'phone_pd_test', 'children', '2020-07-19 11:14:40.00+0000',
     '{"application": "test_app_2"}'),
    ('id5', 'disp', 'phone_pd_test', 'children', '2020-07-19 11:14:50.00+0000',
     '{"application": "test_app_1", "metaqueue": "test_disp_queue_2"}'),
    ('id6', 'disp', 'phone_pd_test', 'children', '2020-07-19 11:14:40.00+0000',
     '{"application": "test_app_1", "metaqueue": "test_disp_queue_1"}');

