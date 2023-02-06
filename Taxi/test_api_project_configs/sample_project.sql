INSERT INTO supportai.project_configs (project_slug, call_service, dispatcher_params) VALUES
('ivr_framework_project', 'ivr_framework', NULL),
('no_dispatcher_params_project', 'voximplant', NULL),
('no_api_key_project', 'voximplant', '{"account_id": 123, "rule_id": 321}'),
('no_account_id_key_project', 'voximplant', '{"api_key": "some_api_key", "rule_id": 321}'),
('good_project', 'voximplant', '{"api_key": "some_api_key", "account_id": 123, "rule_id": 321}');
