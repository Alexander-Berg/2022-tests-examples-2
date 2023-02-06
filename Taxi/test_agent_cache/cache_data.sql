INSERT INTO supportai.versions (id, project_slug, version, draft, hidden, percentage) VALUES
(1, 'sunlight', 0, FALSE, FALSE, 0),
(2, 'sunlight', 1, FALSE, FALSE, 100),
(3, 'sunlight', 100, TRUE, FALSE, 0),
(4, 'ya_market_support', 0, FALSE, FALSE, 100),
(5, 'ya_market_support', 1, FALSE, FALSE, 0);

ALTER SEQUENCE supportai.versions_id_seq RESTART WITH 6;

INSERT INTO supportai.models (id, project_slug, version_id, model_title, model_slug, model_version) VALUES
(1, 'sunlight', 1, 'test_model', 'test_model', '1'),
(2, 'sunlight', 2, 'test_model', 'test_model', '1'),
(3, 'sunlight', 3, 'test_model', 'test_model', '1'),
(4, 'ya_market_support', 4, 'test_model', 'test_model', '1'),
(5, 'ya_market_support', 5, 'test_model', 'test_model', '1');

ALTER SEQUENCE supportai.models_id_seq RESTART WITH 6;

INSERT INTO supportai.topics (id, parent_id, version_id, project_slug, slug, title, rule) VALUES
(1, NULL, 2, 'sunlight', 'topic1', 'Тема 1', 'model_sure_topic is "topic1"'),
(2, NULL, 3, 'sunlight', 'topic1', 'Тема 1', 'model_sure_topic is "topic1"'),
(3, 2, 3, 'sunlight', 'topic2', 'Тема 2', 'model_sure_topic is "topic2"');

ALTER SEQUENCE supportai.topics_id_seq RESTART WITH 4;

INSERT INTO supportai.features (
    id,
    project_slug,
    version_id,
    slug,
    description,
    type,
    domain,
    clarification_type
)
VALUES
(1, 'sunlight', 2, 'feature1', 'Feature 1', 'int', '{"1", "2"}', 'external'),
(2, 'sunlight', 3, 'feature1', 'Feature 1', 'int', '{"1", "2"}', 'external'),
(3, 'sunlight', 3, 'feature2', 'Feature 2', 'float', '{"0.1", "0.2"}', 'external');

ALTER SEQUENCE supportai.features_id_seq RESTART WITH 4;

INSERT INTO supportai.lines (id, project_slug, version_id, slug) VALUES
(1, 'sunlight', 2, 'line1'),
(2, 'sunlight', 3, 'line1'),
(3, 'sunlight', 3, 'line2');

ALTER SEQUENCE supportai.lines_id_seq RESTART WITH 4;

INSERT INTO supportai.tags (id, project_slug, version_id, slug) VALUES
(1, 'sunlight', 2, 'tag1'),
(2, 'sunlight', 3, 'tag1'),
(3, 'sunlight', 3, 'tag2');

ALTER SEQUENCE supportai.tags_id_seq RESTART WITH 4;

INSERT INTO supportai.scenarios (
     id,
     project_slug,
     version_id,
     topic_id,
     title,
     rule_value_parts,
     available
)
VALUES
(1, 'sunlight', 2, 1, 'Сценарий 1 1й тематики', '{"feature1 = 1"}', True),
(2, 'sunlight', 3, 2, 'Сценарий 1 1й тематики', '{"feature1 = 1"}', True),
(3, 'sunlight', 3, 3, 'Сценарий 1 2й тематики', '{"feature2 = 2"}', True);

ALTER SEQUENCE supportai.scenarios_id_seq RESTART WITH 4;

INSERT INTO supportai.policy_actions (
    project_slug,
    version_id,
    scenario_id,
    action_type,
    action_parameters
)
VALUES
('sunlight', 2, 1, 'response', $${"texts": ["Feature1 is 1"], "close": true, "forward_line": "line1"}$$),
('sunlight', 3, 2, 'response', $${"texts": ["Feature1 is 1"], "close": true, "forward_line": "line1"}$$),
('sunlight', 3, 3, 'response', $${"texts": ["Feature2 is 2"], "close": false, "forward_line": "line2"}$$);

INSERT INTO supportai.scenario_tag (scenario_id, tag_id, version_id)
VALUES
(1, 1, 2),
(2, 2, 3),
(3, 3, 3);

INSERT INTO supportai.scenario_feature_order(scenario_id, feature_id, order_index, version_id)
VALUES
(1, 1, 1, 2),
(2, 2, 1, 3);

INSERT INTO supportai.model_topics(project_slug, version_id, slug, threshold)
VALUES
('sunlight', 2, 'topic1', 0.8),
('sunlight', 3, 'topic1', 0.7),
('sunlight', 3, 'topic2', 0.5);

INSERT INTO supportai.custom_configs (
    project_slug,
    version_id,
    value
)
VALUES
('sunlight', 2, $${
    "nlg": {
        "do_greeting_feature_name": "custom_greeting_name",
        "language_to_default_greeting": {
            "ru": "Привет!"
        }
    },
    "nlu": {
        "entities": [{
            "name": "entity1",
            "extractor": {
                "name": "regular_expression",
                "params": {
                  "regular_expression": "5\\d{9}"
                }
            }
        }]
    },
    "dst": {
        "features": [
            {
                "key": "order_ids",
                "type": "int",
                "entity": "entity1",
                "is_array": false,
                "can_be_found_without_question": true
            }
        ]
    }
}$$);

INSERT INTO supportai.scenario_graph
(
 id, project_slug, version_id, topic_id, title, group_name
)
VALUES
(
 1, 'sunlight', 2, 1, 'Первый граф', 'main'
);

INSERT INTO supportai.scenario_graph_node
( id, node_id, version, type, scenario_id, hash)
VALUES
(
 1, 'XXXX', 'XX.XX', 'close', 1, 0
);

INSERT INTO supportai.scenario_graph_actions
( id, project_slug, version_id, node_id, action_type, action_parameters)
VALUES
(
 1, 'sunlight', 2, 1, 'close', '{}'
);

INSERT INTO supportai.scenario_graph_link
(
 id, from_id, to_id, scenario_id
)
VALUES
(
 1, '', 'XXXX', 1
);
