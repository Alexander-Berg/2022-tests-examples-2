INSERT INTO supportai.project_configs (project_slug, call_service) VALUES
('sample_project', 'ivr_framework'),
('some_project', 'ivr_framework'),
('separate_calls_results', 'ivr_framework'),
('expose_first', 'ivr_framework'),
('expose_first_and_second', 'ivr_framework'),
('expose_first_second_and_list', 'ivr_framework'),
('side_project_with_initiated_calls', 'ivr_framework');

INSERT INTO supportai.project_configs (project_slug, call_service, dispatcher_params) VALUES
('project_voximplant', 'voximplant', '{"account_id": 1, "rule_id": 1, "api_key": "1"}');

INSERT INTO supportai.outgoing_calls (project_slug, task_id, chat_id, phone, personal_phone_id, features, status, created, initiated) VALUES
('sample_project', '1', '1', 'phone1', 'id1', '[{"key": "one", "value": "one_1"}, {"key": "two", "value": "two_1"}]', 'ended', '2021-04-01 09:58:01+03', '2021-04-01 09:59:01+03'),
('sample_project', '1', '2', 'phone2', 'id2', '[{"key": "one", "value": "one_2"}, {"key": "two", "value": "two_2"}, {"key": "three", "value": "three_2"}]', 'ended', '2021-04-01 09:58:02+03', '2021-04-01 09:59:01+03'),
('sample_project', '1', '3', 'phone3', 'id3', '[{"key": "one", "value": "one_3"}, {"key": "four", "value": "four_3"}]', 'cancelled', '2021-04-01 09:58:03+03', '2021-04-01 09:59:01+03'),
('sample_project', '2', '4', '1', '1', '{}', 'queued', '2021-01-01 15:00:00+03', NULL),
('sample_project', '2', '5', '2', '2', '{}', 'queued', '2021-01-01 15:00:00+03', NULL),
('sample_project', '2', '6', '3', '3', '{}', 'queued', '2021-01-01 15:00:00+03', NULL),
('sample_project', '2', '7', '4', '4', '{}', 'queued', '2021-01-01 15:00:00+03', NULL),
('expose_first', '4', 'chat1', 'phone1', '1', '[{"key": "initial", "value": "initial1"}]', 'initiated', '2021-01-01 15:00:00+03', '2021-01-01 15:00:00+03'),
('expose_first', '4', 'chat2', 'phone2', '2', '[{"key": "initial", "value": "initial2"}, {"key": "one_more_initial", "value": "one_more_initial2"}]', 'initiated', '2021-01-01 15:00:00+03', '2021-01-01 15:00:00+03'),
('expose_first_and_second', '5', 'chat1', 'phone1', '1', '[{"key": "initial", "value": "initial"}, {"key": "first", "value": "original_first_value"}]', 'initiated', '2021-01-01 15:00:00+03', '2021-01-01 15:00:00+03'),
('project_with_synthesis', '6', 'chat1', '1', '1', '[]', 'ended', '2021-01-01 15:00:00+03', '2021-01-01 15:00:00+03'),
('project_with_version', '7', 'chat1', '1', '1', '[]', 'ended', '2021-01-01 15:00:00+03', '2021-01-01 15:00:00+03'),
('expose_first_second_and_list', '8', 'chat1', 'phone1', '1', '[{"key": "initial", "value": "initial"}, {"key": "first", "value": "original_first_value"}]', 'initiated', '2021-01-01 15:00:00+03', '2021-01-01 15:00:00+03');

INSERT INTO supportai.external_phone_ids (project_slug, external_phone_id, phone)
VALUES
('sample_project', '11', '88005553535'),
('sample_project', '22', '+74959379992'),
('sample_project', '33', '+74957397000'),
('sample_project', '44', '+79101234567'),
('sample_project', '55', '+79107654321');
