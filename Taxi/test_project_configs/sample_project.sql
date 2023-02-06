INSERT INTO supportai.files (id, project_slug, filename, content_type, data) VALUES
(1, 'ivr_framework_with_template_file', 'template_file', 'content_type', '\x00');

ALTER SEQUENCE supportai.files_id_seq RESTART WITH 2;

INSERT INTO supportai.project_configs (project_slug, call_service, template_file_id, dispatcher_params) VALUES
('ivr_framework_no_template_file', 'ivr_framework', NULL, NULL),
('ivr_framework_with_template_file', 'ivr', 1, NULL),
('vox_no_template_file', 'voximplant', NULL, '{"api_key": "some_api", "account_id": 123, "rule_id": 321}');

INSERT INTO supportai.project_configs (project_slug, call_service, audio_files_secret) VALUES
('ivr_framework_no_secret', 'ivr', NULL),
('ivr_framework_with_secret', 'ivr', '0987654321');
