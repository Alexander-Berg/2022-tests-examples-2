INSERT INTO callcenter_qa.feedbacks
(id, created_at, yandex_uid, type, project, external_info)
VALUES ('id1', '2020-07-19 11:13:59.00+0000', 'test_uid_1', 'children', 'call_center',
        '{"feedback_info": {"project": "test_project_1"}, "call_info": {"application": "test_app", "personal_phone_id": "test_phone_pd_id"}}'),
       ('id2', '2020-07-19 11:13:58.00+0000', 'test_uid_2', 'children', 'call_center',
        '{"feedback_info": {"project": "test_project_1"}, "call_info": {"application": "test_app", "personal_phone_id": "test_phone_pd_id"}}'),
       ('id3', '2020-07-19 11:13:59.00+0000', 'test_uid_3', 'children', 'call_center',
        '{"feedback_info": {"project": "test_project_2"}, "call_info": {"application": "test_app", "personal_phone_id": "test_phone_pd_id"}}'),
       ('id4', '2020-07-19 11:13:58.00+0000', 'test_uid_4', 'children', 'call_center',
        '{"feedback_info": {"project": "test_project_2"}, "call_info": {"application": "test_app", "personal_phone_id": "test_phone_pd_id"}}');


