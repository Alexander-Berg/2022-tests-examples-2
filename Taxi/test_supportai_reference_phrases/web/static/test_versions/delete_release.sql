INSERT INTO supportai.matrix_versions (id, type, project_slug)
VALUES
(1, 'draft', 'test_project'),
(2, 'release', 'test_project'),
(3, 'release', 'test_project');

INSERT INTO supportai.matrix (id, text, vector, type, topic)
VALUES
(1, 'тест', '{0.1, 0.1, 0.1, 0.1}', 'addition', 'test_topic1'),
(2, 'тестик', '{0.2, 0.1, 0.1, 0.1}', 'addition', 'test_topic2'),
(3, 'тестики', '{0.3, 0.1, 0.1, 0.1}', 'addition', 'test_topic3'),
(4, 'тестовый', '{0.4, 0.1, 0.1, 0.1}', 'exception', 'test_topic4'),
(5, 'тестовыыый', '{0.5, 0.1, 0.1, 0.1}', 'exception', 'test_topic2'),
(6, 'теееест', '{0.6, 0.1, 0.1, 0.1}', 'addition', 'test_topic2'),
(7, 'бог тестов', '{0.7, 0.1, 0.1, 0.1}', 'exception', 'test_topic1'),
(8, 'тестики', '{0.8, 0.1, 0.1, 0.1}', 'addition', 'test_topic2'),
(9, 'привет', '{0.9, 0.1, 0.1, 0.1}', 'addition', 'privet');

INSERT INTO supportai.matrix_pointers (matrix_id, version_id)
VALUES
(1, 1),
(2, 1),
(3, 1),
(4, 1),
(5, 1),
(6, 1),
(7, 1),
(8, 1),
(9, 1),
(1, 2),
(2, 2),
(3, 2),
(1, 3),
(2, 3),
(3, 3),
(4, 3),
(5, 3),
(6, 3),
(7, 3),
(8, 3),
(9, 3);

ALTER SEQUENCE supportai.matrix_versions_id_seq RESTART WITH 4;
ALTER SEQUENCE supportai.matrix_id_seq RESTART WITH 10;
ALTER SEQUENCE supportai.matrix_pointers_id_seq RESTART WITH 22;
