-- to avoid id collisions
ALTER SEQUENCE supportai.tags_id_seq RESTART WITH 1000;
ALTER SEQUENCE supportai.features_id_seq RESTART WITH 1000;
ALTER SEQUENCE supportai.lines_id_seq RESTART WITH 1000;
ALTER SEQUENCE supportai.scenarios_id_seq RESTART WITH 1000;

INSERT INTO supportai.features (id, project_slug, version_id, slug, description, type, domain, clarification_type) VALUES
(1, 'ya_lavka', 1, 'feature1', 'Feature 1', 'int', '{"1", "2"}', 'external'),
(2, 'ya_lavka', 1, 'feature2', 'Feature 2', 'float', '{"0.1", "0.2"}', 'external'),
(3, 'ya_lavka', 1, 'feature3', 'Feature 3', 'str', '{"test1", "test2"}', 'external'),
(4, 'ya_lavka', 1, 'feature4', 'Feature 4', 'bool', '{}', 'external'),
(5, 'ya_lavka', 1, 'feature5', 'Feature 5', 'str', '{}', 'external');

INSERT INTO supportai.lines (id, project_slug, version_id, slug) VALUES
(1, 'ya_lavka', 1, 'line1'),
(2, 'ya_lavka', 1, 'line2');

INSERT INTO supportai.tags (id, project_slug, version_id, slug) VALUES
(1, 'ya_lavka', 1, 'tag1'),
(2, 'ya_lavka', 1, 'tag2'),
(3, 'ya_lavka', 1, 'tag3'),
(4, 'ya_lavka', 1, 'tag4'),
(5, 'ya_market', 1, 'complex_tag_slug'),
(6, 'ya_lavka', 1, 'complex_tag_slug');

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
(1, 'ya_lavka', 1, 1, 'Сценарий 1 1й тематики', '{"feature1 and feature2"}',  True),
(2, 'ya_lavka', 1, 3, 'Сценарий 1 3й тематики', '{"True"}', True),
(3, 'ya_lavka', 1, 3, 'Сценарий 2 3й тематики', '{"feature1", "feature2"}',  True),
(4, 'ya_lavka', 1, 2, 'English scenario name', '{"True"}',  True);

INSERT INTO supportai.policy_actions (
    project_slug,
    version_id,
    scenario_id,
    action_type,
    action_parameters,
    action_order
)
VALUES
('ya_lavka', 1, 1, 'response', $${"texts": ["Извините"], "close": true, "forward_line":"line1"}$$, 0),
('ya_lavka', 1, 1, 'change_state', $${"features": [{"key": "feature1", "value": "Feature 1 value"}]}$$, 0),
('ya_lavka', 1, 1, 'some_custom', $${"custom_field": "custom_value"}$$, 1),
('ya_lavka', 1, 2, 'response', $${"texts": ["Спасибо, разберемся"], "close": false, "forward_line":"line2"}$$, 0),
('ya_lavka', 1, 3, 'response', $${"texts": [], "close": false, "delay_value_sec": 60}$$, 0),
('ya_lavka', 1, 4, 'response', $${"texts": [], "close": false, "delay_value_sec": 60}$$, 0);

INSERT INTO supportai.scenario_tag (scenario_id, tag_id, version_id)
VALUES
(1, 1, 1),
(1, 2, 1),
(3, 1, 1),
(3, 3, 1),
(3, 6, 1);

INSERT INTO supportai.scenario_feature_order(scenario_id, feature_id, order_index, version_id)
VALUES
(3, 1, 2, 1),
(3, 2, 1, 1);
