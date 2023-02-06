INSERT INTO supportai.project_configs (project_slug, call_service) VALUES
('test_ivr_framework', 'ivr_framework'),
('test_voximplant', 'voximplant');

INSERT INTO supportai.outgoing_calls
    (id, project_slug, call_service, task_id, chat_id, phone, personal_phone_id, features, status, created, session_id, call_record_id)
VALUES
(1, 'test_ivr_framework', 'ivr_framework', '1', 'chat_id', '+79123456789', 'id', '[{"key": "feature1", "value": "123"}]', 'error', '2021-04-01 09:59:01+03', NULL, 'call_record_id_ivr_framework'),
(2, 'test_voximplant', 'voximplant', '1', 'chat_id', '+79123456789', 'id', '[{"key": "feature1", "value": "123"}]', 'error', '2021-04-01 09:59:01+03', NULL, 'http://voximplant_record_storage/call_record.mp3');

ALTER SEQUENCE supportai.outgoing_calls_id_seq RESTART WITH 3;
