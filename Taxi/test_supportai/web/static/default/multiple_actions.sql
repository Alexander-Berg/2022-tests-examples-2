INSERT INTO supportai.versions (id, project_slug, version, draft, hidden, created) VALUES
(1, 'ya_lavka', 1, TRUE, FALSE, now());

ALTER SEQUENCE supportai.versions_id_seq RESTART WITH 5;

INSERT INTO supportai.models (id, project_slug, version_id, model_title, model_slug, model_version) VALUES
(1, 'ya_lavka', 1, 'test_model', 'test_model', '1');

ALTER SEQUENCE supportai.models_id_seq RESTART WITH 5;

INSERT INTO supportai.topics (id, parent_id, version_id, project_slug, slug, title, rule) VALUES
(1, NULL, 1, 'ya_lavka', 'topic1', 'Тема 1', 'model_sure_topic is "topic1"');

ALTER SEQUENCE supportai.topics_id_seq RESTART WITH 10;

INSERT INTO supportai.scenario_graph (id, project_slug, version_id, topic_id, title, group_name, valid) VALUES
(1, 'ya_lavka', 1, 1, 'my_lovely_graph', 'main', true);

INSERT INTO supportai.scenario_graph_node(id, node_id, version, type, scenario_id, hash) VALUES
(1, 'XXXX', 'XX.XX', 'action', 1, 0),
(2, 'XXXX2', 'XX.XX', 'close', 1, 1);

INSERT INTO supportai.scenario_graph_actions
    (id, project_slug, version_id, node_id, action_type, action_parameters)
VALUES
(1, 'ya_lavka', 1, 1, 'action_1', '{"parameter_1": "value_1", "parameter_2": "value_2"}'),
(2, 'ya_lavka', 1, 1, 'action_2', '{"parameter_3": "value_3"}'),
(3, 'ya_lavka', 1, 1, 'action_3', '{"parameter_4": "value_4", "parameter_5": "value_5"}'),
(4, 'ya_lavka', 1, 2, 'close', '{}');

INSERT INTO supportai.scenario_graph_link
(id, from_id, to_id, scenario_id) VALUES
(1, '', 'XXXX', 1),
(2, 'XXXX', 'XXXX2', 1);
