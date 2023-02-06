INSERT INTO callcenter_qa.feedbacks
(id, created_at, yandex_uid, call_id, call_guid, commutation_id, type, project, binary_data)
VALUES ('id1', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_1', 'ServerError', 'call_center', '{"binary_data": [{"type": "image", "mds_link": "image/test_link"}]}'),
       ('id2', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_2', 'ServerError', 'call_center', '{"type": "image", "mds_link": "image/test_link"}'),
       ('id3', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_3', 'ServerError', 'call_center', '{"binary_data": [{"type": "sip_log", "mds_link": "logs/test_link"}]}'),
       ('id4', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_4', 'ServerError', 'call_center', '{"binary_data": [{"mds_link": "image/test_link"}]}'),
       ('id5', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_5', 'ServerError', 'call_center', '{"binary_data": [{"type": "image"}]}'),
       ('id6', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_6', 'ServerError', 'call_center', '{"binary_data": [{"type": "image", "mds_link": "image/test_link"}]}'),
       ('id7', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_6', 'ServerError2', 'call_center', '{"binary_data": [{"type": "image", "mds_link": "image/test_link_2"}]}'),
       ('id8', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_7', 'ServerError2', 'call_center', NULL),
       ('id9', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_7', 'ServerError', 'call_center', '{"binary_data": [{"type": "image", "mds_link": "image/test_link"}]}'),
       ('id10', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_8', 'ServerError2', 'call_center', NULL),
       ('id11', '2020-07-19 11:13:16.425000', 'test_uid', 'call_id_1', 'call_guid_1', 'commutation_id_test_8', 'ServerError', 'call_center', '{"binary_data": [{"type": "image"}]}');
