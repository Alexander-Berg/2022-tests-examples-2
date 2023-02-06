INSERT INTO supportai.clustering_results (id, project_slug, text, cluster_number, score) VALUES
(1, 'test_slug', 'Текст 1', 1, 0.1),
(2, 'test_slug', 'Текст 2', 1, 0.2),
(3, 'test_slug', 'Текст 3', 1, 0.3);

ALTER SEQUENCE supportai.projects_id_seq RESTART WITH 4;
