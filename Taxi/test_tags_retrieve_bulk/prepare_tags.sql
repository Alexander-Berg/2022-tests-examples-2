BEGIN;

INSERT INTO callcenter_qa.tags
(uuid, project, personal_phone_id, reason, blocked_until, created_at, extra)
VALUES
    ('uuid1', 'disp', '+79161234567_id', 'children', '2020-07-19 11:14:40.00+0000', '2020-07-15 11:14:40.00+0000',
     '{"application": "test_app_1", "metaqueue": "test_disp_queue_1"}'),
    ('uuid2', 'disp', '+79161234567_id', 'children', '2020-07-19 11:13:40.00+0000', '2020-07-15 11:13:40.00+0000',
     '{"application": "test_app_1", "metaqueue": "test_disp_queue_1"}'),
    ('uuid3', 'disp', 'phone_pd_test_2', 'children', '2020-07-19 11:14:40.00+0000', '2020-07-15 11:14:40.00+0000',
     '{"application": "test_app_2", "metaqueue": "test_disp_queue_1"}'),
    ('uuid4', 'help', 'phone_pd_test_2', 'aggressive_driver', '2020-07-19 11:14:40.00+0000', '2020-07-15 11:14:40.00+0000',
     '{"application": "test_app_2"}'),
    ('uuid5', 'disp', 'phone_pd_test_3', 'children', '2020-07-19 11:14:50.00+0000', '2020-07-15 11:15:40.00+0000',
     '{"application": "test_app_1", "metaqueue": "test_disp_queue_2"}'),
    ('uuid6', 'disp', 'phone_pd_test_3', 'children', '2020-07-19 11:14:40.00+0000', '2020-07-15 11:14:40.00+0000',
     '{"application": "test_app_1", "metaqueue": "test_disp_queue_1"}');

INSERT INTO callcenter_qa.tag_links
(tag_uuid, feedback_id)
VALUES
    ('uuid1', 'id1_1'), ('uuid1', 'id1_2'), ('uuid1', 'id1_3'),
    ('uuid2', 'id2_1'), ('uuid2', 'id2_2'), ('uuid3', 'id3_1'),
    ('uuid4', 'id4_1'), ('uuid4', 'id4_2'), ('uuid5', 'id5_1');

INSERT INTO callcenter_qa.feedbacks
(id, created_at, yandex_uid, call_id, call_guid, commutation_id, type, project, binary_data)
VALUES ('id1_1', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_1', 'ServerError', 'call_center', '{"binary_data": [{"type": "image", "mds_link": "image/test_link"}]}'),
       ('id1_2', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_2', 'ServerError', 'call_center', '{"type": "image", "mds_link": "image/test_link"}'),
       ('id1_3', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_3', 'ServerError', 'call_center', '{"binary_data": [{"type": "sip_log", "mds_link": "logs/test_link"}]}'),
       ('id2_1', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_4', 'ServerError', 'call_center', '{"binary_data": [{"mds_link": "image/test_link"}]}'),
       ('id2_2', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_5', 'ServerError', 'call_center', '{"binary_data": [{"type": "image"}]}'),
       ('id3_1', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_6', 'ServerError', 'call_center', '{"binary_data": [{"type": "image", "mds_link": "image/test_link"}]}'),
       ('id4_1', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_6', 'ServerError2', 'call_center', '{"binary_data": [{"type": "image", "mds_link": "image/test_link_2"}]}'),
       ('id4_2', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_7', 'ServerError2', 'call_center', NULL),
       ('id5_1', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_7', 'ServerError', 'call_center', NULL);

COMMIT;
