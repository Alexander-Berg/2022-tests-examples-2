INSERT INTO supportai.matrix_versions (id, type, project_slug)
VALUES
(1, 'release', 'project_1'),
(2, 'release', 'project_1');

INSERT INTO supportai.matrix (id, text, vector, topic)
VALUES
(1, 'text', '{0.1, 0.1, 0.1, 0.1}', 'topic'),
(2, 'text 2', '{0.2, 0.1, 0.1, 0.1}', 'topic'),
(3, 'text 3', '{0.3, 0.1, 0.1, 0.1}', 'topic'),
(4, 'text 4', '{0.4, 0.1, 0.1, 0.1}', 'topic'),
(5, 'text 5', '{0.5, 0.1, 0.1, 0.1}', 'topic'),
(6, 'text 2', '{0.2, 0.2, 0.1, 0.1}', 'topic'),
(7, 'text 3', '{0.3, 0.2, 0.1, 0.1}', 'topic'),
(8, 'text 4', '{0.4, 0.2, 0.1, 0.1}', 'topic'),
(9, 'text 5', '{0.5, 0.2, 0.1, 0.1}', 'topic');

INSERT INTO supportai.matrix_pointers (matrix_id, version_id)
VALUES
(1, 1),
(2, 1),
(3, 1),
(4, 1),
(5, 1),
(6, 2),
(7, 2),
(8, 2),
(9, 2);


ALTER SEQUENCE supportai.matrix_id_seq RESTART WITH 15;
ALTER SEQUENCE supportai.matrix_versions_id_seq RESTART WITH 15;
ALTER SEQUENCE supportai.matrix_pointers_id_seq RESTART WITH 15;
