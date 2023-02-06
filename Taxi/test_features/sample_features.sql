INSERT INTO supportai.entities (id, project_slug, version_id, slug, title, type, extractor, extractor_parameters)
VALUES
(1, 'ya_lavka', 1, 'entity1', 'Entity 1', 'str', 'extr1', '{}'::jsonb),
(2, 'ya_lavka', 1, 'entity2', 'Entity 2', 'int', 'extr2', '{}'::jsonb);

ALTER SEQUENCE supportai.entities_id_seq RESTART WITH 3;

ALTER SEQUENCE supportai.features_id_seq RESTART WITH 1000;

INSERT INTO supportai.features (
    id,
    project_slug,
    version_id,
    slug,
    description,
    type,
    domain,
    clarification_type,
    force_question,
    clarifying_question,
    entity_id,
    entity_extract_order
)
VALUES
(1, 'ya_lavka', 1, 'feature1', 'Feature 1', 'int', '{"1", "2"}', 'external', NULL, NULL, NULL, NULL),
(2, 'ya_lavka', 1, 'feature2', 'Feature 2', 'float', '{"0.1", "0.2"}', 'external', NULL,NULL, NULL, NULL),
(3, 'ya_lavka', 1, 'feature3', 'Feature 3', 'str', '{"test1", "test2"}', 'external', NULL, NULL, NULL, NULL),
(4, 'ya_lavka', 1, 'feature4', 'Feature 4', 'bool', '{}', 'external', NULL, NULL, NULL, NULL),
(5, 'ya_taxi', 4, 'feature5', 'Feature 5', 'str', '{}', 'external', NULL, NULL, NULL, NULL),
(6, 'ya_taxi', 4, 'feature6', 'Feature 6', 'str', '{}', 'from_text', false, NULL, 2, 0),
(7, 'ya_taxi', 4, 'feature7', 'Feature 7', 'str', '{}', 'from_text', true, 'Clarify feature 6', 2, 0),
(8, 'ya_taxi', 4, 'feature8', 'Feature 8', 'str', '{}', 'from_text', false, NULL, 2, 0);


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
(1, 'ya_lavka', 1, 1, 'Сценарий 1 1й тематики', '{"feature1 and feature2"}',  True);

INSERT INTO supportai.policy_actions (
    project_slug,
    version_id,
    scenario_id,
    action_type,
    action_parameters
)
VALUES
('ya_lavka', 1, 1, 'response', $${"texts": [], "close": true}$$);


INSERT INTO supportai.scenario_feature_order(scenario_id, feature_id, order_index, version_id)
VALUES
(1, 1, 2, 1),
(1, 2, 1, 1);
