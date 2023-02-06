INSERT INTO supportai.tokens
(project_id, token, allowed_ips)
VALUES
('sample_project', 'XXX', '{"127.0.0.1"}'),
('livetex_project', 'XXX', '{"127.0.0.1"}'),
('idle_project', 'XXX', '{"127.0.0.1"}'),
('project_without_token', NULL, '{"0.0.0.0/0"}'),
('some_project', NULL, '{"0.0.0.0/0"}');
