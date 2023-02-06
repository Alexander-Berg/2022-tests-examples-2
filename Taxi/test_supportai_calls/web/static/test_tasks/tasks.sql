INSERT INTO supportai.tasks (id, project_slug, type, created, file_id, status, error_message, name, params, user_id) VALUES
(1, 'test', 'outgoing_calls_init', '2021-01-01 14:00:00+03', NULL, 'error', 'Error message', 'calls_1', NULL, '1'),
(2, 'test', 'outgoing_calls_init', '2021-01-01 13:00:00+03', NULL, 'completed', NULL, NULL, NULL, NULL),
(3, 'test', 'outgoing_calls_results', '2021-01-01 12:00:00+03', NULL, 'error', NULL, NULL, '{"ref_task_id": 2}', NULL);
