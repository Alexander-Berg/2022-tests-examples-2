INSERT INTO supportai.versions (id, project_slug, version, draft, hidden, percentage) VALUES
(1000, 'ya_lavka', 0, TRUE, FALSE, 0),
(1001, 'ya_lavka', 1, FALSE, FALSE, 0),
(1002, 'ya_lavka', 2, FALSE, FALSE, 100);

INSERT INTO supportai.topics (id, parent_id, version_id, project_slug, slug, title, rule) VALUES
(6, NULL, 1000, 'ya_lavka', 'topic1', 'Тема 1', 'model_sure_topic is "topic1"'),
(7, 6, 1000, 'ya_lavka', 'topic2', 'Тема 2', 'model_sure_topic is "topic2"');
