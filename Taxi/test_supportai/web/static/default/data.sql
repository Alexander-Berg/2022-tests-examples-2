INSERT INTO supportai.entities (
    id,
    project_slug,
    version_id,
    slug,
    title,
    type,
    extractor,
    extractor_parameters
)
VALUES
(1, 'ya_lavka', 1, 'entity1', 'Entity 1', 'str', 'regular_expression', '{"regular_expression": "[a-z]+"}'::jsonb);

ALTER SEQUENCE supportai.entities_id_seq RESTART WITH 2;

INSERT INTO supportai.features (
    id,
    project_slug,
    version_id,
    slug,
    description,
    type,
    is_array,
    domain,
    clarification_type,
    entity_id,
    entity_extract_order
)
VALUES
(1, 'ya_lavka', 1, 'feature1', 'Feature 1', 'int', FALSE, '{"1", "2"}', 'external', NULL, NULL),
(2, 'ya_lavka', 1, 'feature2', 'Feature 2', 'float', FALSE, '{"0.1", "0.2"}', 'external', NULL, NULL),
(3, 'ya_lavka', 1, 'feature3', 'Feature 3', 'str', TRUE, '{}', 'from_text', 1, NULL);

ALTER SEQUENCE supportai.features_id_seq RESTART WITH 4;

INSERT INTO supportai.lines (id, project_slug, version_id, slug) VALUES
(1, 'ya_lavka', 1, 'line1'),
(2, 'ya_lavka', 1, 'line2');

ALTER SEQUENCE supportai.lines_id_seq RESTART WITH 3;

INSERT INTO supportai.tags (id, project_slug, version_id, slug) VALUES
(1, 'ya_lavka', 1, 'tag1'),
(2, 'ya_lavka', 1, 'tag2');

ALTER SEQUENCE supportai.tags_id_seq RESTART WITH 3;

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
(1, 'ya_lavka', 1, 1, 'Сценарий 1 1й тематики', '{"feature1 and feature2"}', True),
(2, 'ya_lavka', 1, 3, 'Сценарий 1 3й тематики', '{"True"}', True);

ALTER SEQUENCE supportai.scenarios_id_seq RESTART WITH 3;

INSERT INTO supportai.policy_actions (
    project_slug,
    version_id,
    scenario_id,
    action_type,
    action_parameters
)
VALUES
('ya_lavka', 1, 1, 'response', $${"texts": [], "close": true, "forward_line": "line1"}$$),
('ya_lavka', 1, 2, 'response', $${"texts": ["Спасибо, разберемся"], "close": false, "forward_line": "line2"}$$);

INSERT INTO supportai.scenario_tag (scenario_id, tag_id, version_id)
VALUES
(1, 1, 1),
(2, 2, 1);

INSERT INTO supportai.scenario_feature_order(scenario_id, feature_id, order_index, version_id)
VALUES
(1, 1, 2, 1),
(1, 2, 1, 1);

INSERT INTO supportai.model_topics(project_slug, version_id, slug, key_metric, threshold)
VALUES
('ya_lavka', 1, 'topic1', 'precision', 0.1),
('ya_lavka', 1, 'topic2', 'precision', 0.2);

INSERT INTO supportai.feature_suggestions(project_slug, feature, updated_at, count, suggestion)
VALUES
('ya_lavka', 'feature1', '2021-08-02T10:00:00', 120, '0'),
('ya_lavka', 'feature1', '2021-08-02T10:00:55', 1, '1'),
('ya_lavka', 'feature1', '2021-08-02T10:00:00', 1, '2'),
('ya_lavka', 'feature1', '2021-08-02T10:00:00', 2, '3'),
('ya_lavka', 'feature2', '2021-08-02T10:00:00', 34, '4');

INSERT INTO supportai.custom_configs (
    project_slug,
    version_id,
    value
)
VALUES
('ya_drive_dialog', 2, $${
    "nlg": {
        "enrich": [
            {
                "if_feature": "do_greeting",
                "add_at": "begin",
                "template": "greeting"
            }
        ],
        "localisations": {
            "greeting": {
                "ru": "Здравствуйте!"
            }
        }
    },
    "nlu": {
        "topics": [{
            "slug": "custom_topic"
        }],
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
}$$),
('ya_lavka', 1, $${
    "nlg": {
        "enrich": [
            {
                "if_feature": "do_greeting",
                "add_at": "begin",
                "template": "greeting"
            }
        ],
        "localisations": {
            "greeting": {
                "ru": "Здравствуйте!"
            }
        },
        "separator_symbol": " ",
        "concatenate_symbol": " ",
        "concatenate_message": true,
        "concatenate_messages": true
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
    "flags": {
        "graph_policy": true,
        "reply_as_texts": true,
        "new_predicate_engine": false
    },
    "policy_graph": {
        "main": {
            "graph": {
                "order_status_new": {
                    "": {"next": "XXXX1"},
                    "XXXX1": {"next": "XXXX2"},
                    "XXXX2": {"next": null},
                    "XXXX3": {"next": "XXXX4"},
                    "XXXX2_true": {"next": "XXXX4"},
                    "XXXX2_false": {"next": "XXXX3"}
                }
            },
            "nodes": {
                "XXXX1": {
                    "type": "action",
                    "action": {
                        "type": "change_state",
                        "parameters": {"features": [{"key": "order_id_d", "value": null}]}
                    }
                },
                "XXXX2": {
                    "type": "condition",
                    "action": {"type": "condition", "parameters": {"node_id": "XXXX2", "predicate": "order_id"}}
                },
                "XXXX3": {"type": "response", "action": {"type": "response", "parameters": {"text": "Подскажите номер вашего заказа?"}}},
                "XXXX4": {"type": "response", "action": {"type": "response", "parameters": {"text": "Cтатус заказа ГОТОВ"}}}}}}}
$$);
