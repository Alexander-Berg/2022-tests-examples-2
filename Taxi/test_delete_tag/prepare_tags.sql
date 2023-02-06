BEGIN;

INSERT INTO callcenter_qa.tags
(uuid, project, personal_phone_id, reason, blocked_until, created_at, extra)
VALUES
    ('uuid1', 'disp', '+79161234567_id', 'children', '2020-07-19 11:14:40.00+0000', '2020-07-15 11:14:40.00+0000',
     '{"application": "test_app_1", "metaqueue": "test_disp_queue_1"}'),
    ('uuid2', 'disp', '+79161234567_id', 'children', '2020-07-19 11:13:40.00+0000', '2020-07-15 11:13:40.00+0000',
     '{"application": "test_app_1", "metaqueue": "test_disp_queue_1"}');

INSERT INTO callcenter_qa.tag_links
(tag_uuid, feedback_id)
VALUES
    ('uuid1', 'id1_1'), ('uuid1', 'id1_2'), ('uuid1', 'id1_3'),
    ('uuid2', 'id2_1'), ('uuid2', 'id2_2');

INSERT INTO callcenter_qa.feedbacks
(id, created_at, yandex_uid, call_id, call_guid, commutation_id, type, project, binary_data, enabled_for_aggregation)
VALUES ('id1_1', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_1', 'ServerError', 'call_center', '{"binary_data": [{"type": "image", "mds_link": "image/test_link"}]}', true),
       ('id1_2', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_2', 'ServerError', 'call_center', '{"type": "image", "mds_link": "image/test_link"}', true),
       ('id1_3', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_3', 'ServerError', 'call_center', '{"binary_data": [{"type": "sip_log", "mds_link": "logs/test_link"}]}', true),
       ('id2_1', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_4', 'ServerError', 'call_center', '{"binary_data": [{"mds_link": "image/test_link"}]}', true),
       ('id2_2', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_5', 'ServerError', 'call_center', '{"binary_data": [{"type": "image"}]}', true);

COMMIT;
