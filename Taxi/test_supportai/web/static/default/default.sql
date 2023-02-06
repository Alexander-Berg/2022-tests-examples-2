
INSERT INTO supportai.versions (id, project_slug, version, draft, hidden, created) VALUES
(1, 'ya_lavka', -1, TRUE, FALSE, now()),
(2, 'ya_market', -1, TRUE, FALSE, now()),
(3, 'ya_taxi', -1, TRUE, FALSE, now()),
(4, 'ya_taxi', 0, TRUE, FALSE, now() + interval '1' second );

ALTER SEQUENCE supportai.versions_id_seq RESTART WITH 5;

INSERT INTO supportai.models (id, project_slug, version_id, model_title, model_slug, model_version) VALUES
(1, 'ya_lavka', 1, 'test_model', 'test_model', '1'),
(2, 'ya_market', 2, 'test_model', 'test_model', '1'),
(3, 'ya_taxi', 3, 'test_model', 'test_model', '1'),
(4, 'ya_taxi', 4, 'test_model', 'test_model', '1');

ALTER SEQUENCE supportai.models_id_seq RESTART WITH 5;

INSERT INTO supportai.topics (id, parent_id, version_id, project_slug, slug, title, rule) VALUES
(1, NULL, 1, 'ya_lavka', 'topic1', 'Тема 1', 'model_sure_topic is "topic1"'),
(2, 1, 1, 'ya_lavka', 'topic2', 'Тема 2', 'model_sure_topic is "topic2"'),
(3, 1, 1, 'ya_lavka', 'topic3', 'Тема 3', 'model_sure_topic is "topic3"'),
(4, 2, 1, 'ya_lavka', 'topic4', 'Тема 4', 'model_sure_topic is "topic4"'),
(5, NULL, 3, 'ya_taxi', 'topic5', 'Тема 5', 'model_sure_topic is "topic5"');

ALTER SEQUENCE supportai.topics_id_seq RESTART WITH 10;
