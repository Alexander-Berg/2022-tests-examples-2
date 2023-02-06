INSERT INTO supportai.tasks (id, project_id, type, created, file_id, status, error_message, name, params, user_id) VALUES
(1, 1, 'export', '2021-01-01 15:00:00+03', NULL, 'error', 'Тест ошибки', NULL, NULL, 1),
(2, 1, 'outgoing_calls_init', '2021-01-01 14:00:00+03', NULL, 'created', NULL, 'calls_1', NULL, 1),
(3, 1, 'outgoing_calls_init', '2021-01-01 13:00:00+03', NULL, 'created', NULL, NULL, NULL, NULL),
(4, 1, 'outgoing_calls_results', '2021-01-01 12:00:00+03', NULL, 'error', NULL, NULL, '{"ref_task_id": "2"}', NULL),
(5, 1, 'outgoing_calls_results', '2021-01-01 12:00:00+03', NULL, 'created', NULL, NULL, '{"results_from_separate_calls": true}', NULL);
