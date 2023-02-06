INSERT INTO supportai.project_configs (project_slug, call_service, auth_token, auth_allowed_ips) VALUES
('test', 'ivr_framework', NULL, NULL),
('test1', 'ivr_framework', 'test_token', '{"127.0.0.1"}'),
('test2', 'ivr_framework', NULL, NULL),
('test3', 'ivr_framework', NULL, '{"0.0.0.0/0"}'),
('test_ignore_ivr_framework', 'ivr_framework', NULL, NULL),
('test_ignore_features_exposure', 'ivr_framework', NULL, NULL),
('test_ignore_voximplant', 'voximplant', NULL, NULL),
('various_call_service', 'ivr_framework', NULL, NULL),
('test_register_incoming_call', 'ivr_framework', NULL, NULL);

INSERT INTO supportai.external_phone_ids (project_slug, external_phone_id, phone) VALUES
('test_ignore_ivr_framework', 'ext_1', '79991234567');


INSERT INTO supportai.outgoing_calls (id, project_slug, call_service, chat_id, phone, personal_phone_id, features, status, created, call_record_id) VALUES
(1, 'various_call_service', 'ivr_framework', '2', '2', '2', '{}', 'ended', '2021-04-01 09:59:02+03', 'ivr_framework_call_record_id');


INSERT INTO supportai.outgoing_calls (id, project_slug, call_service, task_id, chat_id, phone, personal_phone_id, features, status, created, initiated, session_id, call_record_id) VALUES
(2, 'test_ignore_ivr_framework', 'ivr_framework', '1', 'chat1', 'phone1', 'id1', '{}', 'ended', '2021-04-01 09:59:01+03', '2021-04-01 09:59:02+03', NULL, 'call_record_id_ivr_framework'),
(3, 'test_ignore_voximplant', 'voximplant', '1', 'chat1', '1', '1', '[]', 'ended', '2021-04-01 09:59:01+03', '2021-04-01 09:59:01+03', NULL, 'https://records_for_vox_project/5.mp3');

ALTER SEQUENCE supportai.outgoing_calls_id_seq RESTART WITH 4;


INSERT INTO supportai.outgoing_calls (project_slug, task_id, chat_id, phone, personal_phone_id, features, status, created) VALUES
('test_ignore_ivr_framework', '2', 'chat2', 'phone1', 'id1', '[]', 'initiated', '2021-01-01 15:00:00+03'),
('test_ignore_ivr_framework', '2', 'chat3', 'phone1', 'id1', '[]', 'queued', '2021-01-01 15:00:00+03'),
('test_ignore_ivr_framework', '2', 'chat4', 'phone1', 'id1', '[]', 'error', '2021-01-01 15:00:00+03'),
('test_ignore_ivr_framework', '2', 'chat5', 'phone1', 'id1', '[]', 'queued', '2021-01-01 15:00:00+03'),
('test_ignore_features_exposure', '3', 'chat1', 'phone1', 'id1', '[]', 'queued', '2021-01-01 15:00:00+03');
