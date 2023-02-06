INSERT INTO supportai.tokens (project_id, token, allowed_ips)
VALUES
('detmir_dialog', NULL, '{"0.0.0.0/0"}');

INSERT INTO supportai.async_tasks (id, project_id, chat_id, wait_until)
VALUES
(1, 'detmir_dialog', '4321', '2021-01-01 15:00:00+03');

ALTER SEQUENCE supportai.async_tasks_id_seq RESTART WITH 2;
