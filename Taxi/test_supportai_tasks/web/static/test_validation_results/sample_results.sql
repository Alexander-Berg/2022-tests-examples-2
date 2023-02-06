INSERT INTO supportai.tasks (id, project_id, type, created, file_id, status) VALUES
(1, 1, 'validation', '2021-01-01T15:00:00', NULL, 'completed');

INSERT INTO supportai.validation_results (project_id, task_id, metric, production_value, testing_value, difference) VALUES
(1, 1, 'metric1', 0.8, 0.9, 0.1),
(1, 1, 'metric2', 0.5, 0.8, 0.3);
