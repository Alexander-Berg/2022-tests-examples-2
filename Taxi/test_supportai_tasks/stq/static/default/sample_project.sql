INSERT INTO supportai.projects (id, slug, title, validation_instance_id, new_config_schema) VALUES
(1, 'sample_project', 'Пример проекта', 'workflow/instance', FALSE),
(2, 'sample_project_without_inst', 'Пример проекта без таски валидации', NULL, FALSE),
(3, 'sample_project_new_config', 'Пример проекта с конфигом в supportai', NULL, TRUE);

ALTER SEQUENCE supportai.projects_id_seq RESTART WITH 4;

INSERT INTO supportai.tasks (id, project_id, type, created, file_id, name) VALUES
(1, 1, 'deploy', '2021-01-01 15:00:00+03', NULL, NULL),
(2, 1, 'export', '2021-01-01 15:00:00+03', NULL, NULL),
(3, 1, 'validation', '2021-01-01 15:00:00+03', NULL, NULL),
(5, 2, 'validation', '2021-01-01 15:00:00+03', NULL, NULL),
(6, 3, 'deploy', '2021-01-01 15:00:00+03', NULL, NULL),
(7, 3, 'test_configuration', '2021-01-01 15:00:00+03', NULL, NULL),
(8, 2, 'test_configuration', '2021-01-01 15:00:00+03', NULL, NULL);

ALTER SEQUENCE supportai.tasks_id_seq RESTART WITH 9;


INSERT INTO supportai.configuration_test (id, task_id, request_text, is_equal) VALUES
(1, 7, 'Здравствуйте!', True),
(2, 7, 'Спасибо!', False),
(3, 7, 'Где мой заказ?', True),
(4, 8, 'Как оставить отзыв?', True);

ALTER SEQUENCE supportai.configuration_test_id_seq RESTART WITH 5;
