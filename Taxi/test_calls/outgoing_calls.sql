INSERT INTO supportai.project_configs (project_slug) VALUES
('test_get_calls');

INSERT INTO supportai.outgoing_calls (id, project_slug, task_id, chat_id, phone, personal_phone_id, features, status, created, initiated) VALUES
(1, 'test', '1', 'chat1', 'phone1', 'id1', '[]', 'queued', '2021-04-01 09:57:01+03', NULL),
(2, 'test', '1', 'chat2', 'phone2', 'id2', '[]', 'queued', '2021-04-01 09:57:01+03', NULL),
(3, 'test', '1', '3', 'phone3', 'id3', '[]', 'ended', '2021-04-01 09:58:01+03', '2021-04-01 09:59:01+03'),
(4, 'test', '2', '4', '+79123456789', 'id4', '[{"key": "feature1", "value": "123"}]', 'error', '2021-04-01 09:59:01+03', '2021-04-01 09:59:55+03'),
(5, 'test_features_exposure', '3', 'chat2', 'phone2', 'id2', '[]', 'ended', '2021-04-01 09:58:01+03', '2021-04-01 09:59:01+03'),
(6, 'test2', '1', '2', 'phone2', 'id2', '[]', 'ended', '2021-04-01 09:58:01+03', '2021-04-01 09:59:01+03');

ALTER SEQUENCE supportai.outgoing_calls_id_seq RESTART WITH 7;
