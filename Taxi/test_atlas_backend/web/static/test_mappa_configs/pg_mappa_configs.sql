INSERT INTO taxi_db_postgres_atlas_backend.mappa_configs (
    code,
    config
)
VALUES (
    'test_config_1',
    '
    {
        "map": {
            "layers": [{"layer_prop_1": {}, "layer_prop_2": {}}],
            "features": [{"map_feature_prop": {}}],
            "defaultZoom": 0,
            "defaultPosition": [0, 0]
        },
        "meta": {
            "id": "id_1",
            "code": "test_config_1",
            "name": "1",
            "created_at": 0,
            "updated_at": 0,
            "author_login": "raifox",
            "core_version": "1.0"
        },
        "features": [{"feature_prop": {}}],
        "classifiers": [
            {
                "id": "c_1",
                "name": "classifier_1",
                "options": [{"type": "number", "label": "classifier_option", "value": 1.0}]
            }
        ]
    }
    '
),
(
    'test_config_2',
    '
    {
        "map": {
            "layers": [{"layer_prop_1": {}, "layer_prop_2": {}}],
            "features": [{"map_feature_prop": {}}],
            "defaultZoom": 0,
            "defaultPosition": [0, 0]
        },
        "meta": {
            "id": "id_2",
            "code": "test_config_2",
            "name": "2",
            "created_at": 0,
            "updated_at": 0,
            "author_login": "test_user",
            "core_version": "1.0"
        },
        "features": [{"feature_prop": {}}],
        "classifiers": [
            {
                "id": "c_1",
                "name": "classifier_1",
                "options": [{"type": "number", "label": "classifier_option", "value": 1.0}]
            }
        ]
    }
    '
),
(
    'test_config_3',
    '
    {
        "map": {
            "layers": [{"layer_prop_1": {}, "layer_prop_2": {}}],
            "features": [{"map_feature_prop": {}}],
            "defaultZoom": 0,
            "defaultPosition": [0, 0]
        },
        "meta": {
            "id": "id_3",
            "code": "test_config_3",
            "name": "3",
            "created_at": 0,
            "updated_at": 0,
            "author_login": "raifox",
            "core_version": "1.0"
        },
        "features": [{"feature_prop": {}}],
        "classifiers": [
            {
                "id": "c_1",
                "name": "classifier_1",
                "options": [{"type": "number", "label": "classifier_option", "value": 1.0}]
            }
        ]
    }
    '
),
(
    'test_config_4',
    '
    {
        "map": {
            "layers": [{"layer_prop_1": {}, "layer_prop_2": {}}],
            "features": [{"map_feature_prop": {}}],
            "defaultZoom": 0,
            "defaultPosition": [0, 0]
        },
        "meta": {
            "id": "id_4",
            "code": "test_config_4",
            "name": "4",
            "created_at": 0,
            "updated_at": 0,
            "author_login": "raifox",
            "core_version": "1.0"
        },
        "features": [{"feature_prop": {}}],
        "classifiers": [
            {
                "id": "c_1",
                "name": "classifier_1",
                "options": [{"type": "number", "label": "classifier_option", "value": 1.0}]
            }
        ]
    }
    '
);
