INSERT INTO supportai.versions (id, project_slug, version, draft, hidden, created) VALUES
(1, 'ya_lavka', -1, TRUE, FALSE, now());

INSERT INTO supportai.topics (id, parent_id, version_id, project_slug, slug, title, rule) VALUES
(1, NULL, 1, 'ya_lavka', 'topic1', 'Тема 1', 'model_sure_topic is "topic1"');
