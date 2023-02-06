INSERT INTO supportai.providers (name) VALUES ('test_provider'), ('supportai');

INSERT INTO supportai.users (username, provider, provider_id, is_active, is_superadmin, created_at) VALUES
('test_user', 'test_provider', '123', TRUE, FALSE, '2021-01-01 15:00:00+03'),
('test_user_2', 'supportai', '123', TRUE, FALSE, '2021-01-01 15:00:00+05'),
('admin', 'supportai', '234', TRUE, TRUE, '2021-01-01 15:00:00+07'),
('admin_2', 'supportai', '345', TRUE, TRUE, '2021-01-01 15:00:00+07'),
('admin_3', 'supportai', '456', TRUE, TRUE, '2021-01-01 15:00:00+07'),
('test_user_3', 'test_provider', '234', TRUE, FALSE, '2021-01-01 15:00:00+03'),
('test_user_4', 'supportai', '567', TRUE, FALSE, '2021-01-01 15:00:00+05'),
('test_user_5', 'test_provider', '345', TRUE, FALSE, '2021-01-01 15:00:00+03'),
('test_user_6', 'supportai', '678', TRUE, FALSE, '2021-01-01 15:00:00+05'),
('test_user_7', 'supportai', '789', TRUE, FALSE, '2021-01-01 15:00:00+05');

INSERT INTO supportai.login_data (user_id, password) VALUES
(2, '$2b$12$TRtOPSBaKCiNJLmkoEMPnODXgiD/ycr0Pso6xrhDpqvXHCQCHvoN.');

INSERT INTO supportai.presets (slug, title) VALUES
('test_preset_1', 'Test Preset 1'),
('test_preset_2', 'Test Preset 2'),
('test_preset_3', 'Test Preset 3'),
('test_preset_4', 'Test Preset 4');

INSERT INTO supportai.projects (slug, title, is_chatterbox, validation_instance_id, preset_id) VALUES
('test_project', 'Test Project', FALSE, '', 1),
('test_project_2', 'Test Project 2', FALSE, '', 2),
('test_project_3', 'Test Project 3', FALSE, '', 3);

INSERT INTO supportai.capabilities (slug) VALUES
('test_capability'),
('test_capability_2'),
('test_capability_3'),
('test_capability_4'),
('test_capability_5'),
('admin_capability'),
('admin_capability_2'),
('admin_capability_3'),
('project_capability_1'),
('project_capability_2'),
('project_capability_3');

INSERT INTO supportai.capabilities_to_user (capability, user_id, type) VALUES
('test_capability', 1, 'allowed'),
('test_capability_2', 1, 'blocked'),
('test_capability_3', 1, 'allowed'),
('test_capability', 3, 'allowed'),
('test_capability_2', 3, 'blocked'),
('test_capability_3', 3, 'allowed'),
('test_capability_3', 7, 'allowed'),
('test_capability_4', 7, 'allowed'),
('test_capability_5', 7, 'blocked');

INSERT INTO supportai.capabilities_to_project (capability, project_id, type) VALUES
('project_capability_1', 1, 'allowed'),
('project_capability_2', 1, 'blocked'),
('project_capability_3', 1, 'allowed'),
('project_capability_1', 2, 'blocked'),
('project_capability_2', 2, 'blocked'),
('project_capability_3', 2, 'allowed'),
('project_capability_1', 3, 'allowed'),
('project_capability_2', 3, 'allowed'),
('project_capability_3', 3, 'blocked');

INSERT INTO supportai.roles (id, slug, permissions) VALUES
(1, 'super_admin', '{}'),
(2, 'admin', '{"read","write","modify"}'),
(3, 'editor', '{"read","write"}'),
(4, 'reader', '{"read"}'),
(5, 'read_modifier', '{"read","modify"}'),
(6, 'write_modifier', '{"write", "modify"}'),
(7, 'writer', '{"write"}'),
(8, 'modifier', '{"modify"}'),
(9, 'not_allowed', '{}');

INSERT INTO supportai.capabilities_to_role (capability, role_id, type) VALUES
('admin_capability', 1, 'allowed'),
('admin_capability_2', 1, 'blocked'),
('admin_capability_3', 1, 'allowed'),
('test_capability_4', 3, 'allowed'),
('test_capability_5', 3, 'allowed');

INSERT INTO supportai.user_to_role (user_id, role_id, project_id) VALUES
(2, 4, 1),
(2, 4, 2),
(6, 4, 3),
(7, 4, 3),
(4, 4, 3),
(8, 3, 3),
(9, 3, 3),
(9, 4, 2);

INSERT INTO supportai.capabilities_presets (capability, preset_id, type) VALUES
('test_capability', 1, 'allowed'),
('test_capability_3', 1, 'allowed'),
('project_capability_2', 1, 'blocked'),
('project_capability_3', 1, 'allowed'),
('test_capability_2', 2, 'allowed'),
('test_capability_5', 2, 'blocked'),
('project_capability_3', 2, 'allowed'),
('test_capability_4', 3, 'blocked'),
('test_capability_3', 3, 'allowed'),
('project_capability_1', 3, 'allowed');

INSERT INTO supportai.preset_capabilities (preset_id, capability) VALUES
(1, 'test_capability'),
(1, 'test_capability_3'),
(1, 'test_capability_4'),
(2, 'test_capability_2'),
(2, 'admin_capability_2'),
(2, 'project_capability_1'),
(3, 'test_capability'),
(3, 'test_capability_5'),
(3, 'admin_capability'),
(3, 'project_capability_2');

INSERT INTO supportai.project_users (user_id, project_id, "group") VALUES
(1, 1, 'guest'),
(2, 1, 'guest'),
(4, 1, 'standard'),
(6, 1, 'standard'),
(7, 1, 'admin'),
(2, 2, 'guest'),
(3, 2, 'standard'),
(5, 2, 'standard'),
(8, 2, 'admin');

INSERT INTO supportai.group_capabilities (project_id, "group", capability) VALUES
(1, 'guest', 'test_capability'),
(1, 'guest', 'test_capability_4'),
(1, 'standard', 'test_capability_3'),
(1, 'standard', 'test_capability_4'),
(1, 'admin', 'test_capability'),
(1, 'admin', 'test_capability_3'),
(1, 'admin', 'test_capability_4'),
(2, 'standard', 'test_capability_2'),
(2, 'standard', 'project_capability_1'),
(2, 'admin', 'test_capability_2'),
(2, 'admin', 'admin_capability_2'),
(2, 'admin', 'project_capability_1'),
(3, 'guest', 'test_capability'),
(3, 'admin', 'admin_capability'),
(3, 'admin', 'project_capability_2');

INSERT INTO supportai.api_keys (project_id, api_key) VALUES
(1, 'AsdadasdaQ23r'),
(2, '321232131231'),
(3, '12345678');

INSERT INTO supportai.allowed_ips (project_id, ip_address) VALUES
(1, '127.0.0.1'),
(1, '0.0.0.0'),
(1, '167.2.3.5'),
(2, '172.2.8.6'),
(2, '172.2.8.8'),
(3, '8.8.8.8'),
(3, '9.9.9.9');

INSERT INTO supportai.integrations (slug, check_signature, auth_type, data, modified) VALUES
('test_integration_1', FALSE, 'tvm', '{"ACTION": {"location": "body", "path": "$.action_slug"}}', 390),
('test_integration_2', TRUE, 'tvm', '{"SIGNATURE": {"location": "body", "path": "$.signature"}, "ACTION": {"location": "path", "index": 2}}', 248),
('test_integration_3', FALSE, 'api_key', '{"API_KEY": {"location": "body", "path": "$.api_key"}, "ACTION": {"location": "path", "index": 3}}', 650),
('test_integration_4', TRUE, 'api_key','{"API_KEY": {"location": "query", "param_name": "X-YaTaxi-API-Key"}, "SIGNATURE": {"location": "query", "param_name": "signature"}, "ACTION": {"location": "body", "path": "$.action_id"}}', 340),
('test_integration_5', TRUE, 'ip_address', '{"IP_ADDRESS": {"location": "header", "param_name": "X-Real-IP"}, "SIGNATURE": {"location": "header", "param_name": "Signature"}, "ACTION": {"location": "query", "param_name": "action_id"}}', 870);

INSERT INTO supportai.actions (integration_id, slug, is_ignored, request_mapping, response_mapping, modified) VALUES
(1, 'test_action_1', FALSE, '{"key": "value"}', '{}', 630),
(1, 'test_action_2', TRUE, '{}', '{"response": "some awesome mapping!!!"}', 275),
(3, 'test_action_3', TRUE, '{"key_1": "value_1", "key_2": "value_2"}', '{}', 670),
(3, 'test_action_4', TRUE, '{"key": "value"}', '{}', 92),
(3, 'test_action_5', FALSE, '{}', '{}', 730),
(4, 'test_action_6', FALSE, '{}', '{}', 268);

INSERT INTO supportai.callbacks (action_id, condition, uri, request_method, request_mapping, modified) VALUES
(1, 'reply', '/', 'GET', '{}', 232),
(1, 'tag', '/some_slug', 'POST', '{"message": "Awwww, infinite loops, my pleasure"}', 138),
(1, 'tag', '/another_slug', 'DELETE', '{}', 225),
(2, 'close', '/', 'DELETE', '{"message": "Do not delete anything"}', 873),
(3, 'forward', '/sluggy_slug', 'GET', '{}', 674),
(5, 'reply_iterable', '/', 'GET', '{}', 89),
(5, 'forward', '/', 'POST', '{"message": "Awesome POST session"}', 301),
(6, 'tag', '/', 'GET', '{}', 208);

INSERT INTO supportai.project_integrations (project_id, integration_id, base_url, secret_data) VALUES
(1, 1, NULL, '{}'),
(1, 2, 'https://baseurl.com', '{"SIGNATURE_TOKEN": "token-token"}'),
(1, 3, 'https://anotherawesomeurl.com', '{"API_KEY": "keeeeeeeey"}'),
(2, 4, 'https://urlurlurl.com', '{"API_KEY": "keykeykey"}'),
(3, 5, 'https://urlurl.com', '{"API_KEY": "kkkey", "SIGNATURE_TOKEN": "tik-tak-token"}');
