INSERT INTO dispatch_settings.zones (zone_name)
VALUES ('__default__'),
       ('test_zone_1'),
       ('test_zone_2'),
       ('test_zone_3'),
       ('test_zone_4');

INSERT INTO dispatch_settings.groups (name, description) VALUES ('base', 'description'), ('another_base', 'description');

INSERT INTO dispatch_settings.tariffs (tariff_name, group_id)
VALUES ('__default__base__', (SELECT id FROM dispatch_settings.groups WHERE name = 'base')),
       ('test_tariff_1', NULL),
       ('test_tariff_2', NULL),
       ('test_tariff_3', NULL),
       ('test_tariff_4', (SELECT id FROM dispatch_settings.groups WHERE name = 'another_base'));

-- Copied from V01__dispatch_settings.sql
-- Cause of testsuite postgres workflow
INSERT INTO dispatch_settings.parameters (field_name, schema)
VALUES
( -- SEARCH_SETTINGS_CLASSES
    'AIRPORT_QUEUE_DISPATCH_BONUS_MAX',
    '{"type": "integer", "maximum": 0}'
),
(
    'AIRPORT_QUEUE_DISPATCH_BONUS_MIN',
    '{"type": "integer", "maximum": 0}'
),
(
    'AIRPORT_QUEUE_DISPATCH_BONUS_STEP',
    '{"type": "integer", "maximum": 0}'
),
(
    'ANTISURGE_BONUS_COEF',
    '{"type": "number", "minimum": 0}'
),
(
    'ANTISURGE_BONUS_GAP',
    '{"type": "integer", "minimum": 0}'
),
(
    'APPLY_ETA_ETR_IN_CAR_RANGING',
    '{"type": "boolean"}'
),
(
    'DISPATCH_DRIVER_TAGS_BLOCK',
    '{"type": "array", "items": {"type": "string"}}'
),
(
    'DISPATCH_DRIVER_TAGS_BONUSES',
    '{"type": "object", "required": ["__default__"], "additionalProperties": {"type": "integer"}}'
),
(
    'DISPATCH_GRADE_BONUS_SECONDS',
    '{"type": "object", "required": ["__default__"], "additionalProperties": {"type": "integer"}}'
),
(
    'DISPATCH_HOME_BONUS_SECONDS',
    '{"type": "integer"}'
),
(
    'DISPATCH_MAX_POSITIVE_BONUS_SECONDS',
    '{"type": "integer", "minimum": 0}'
),
(
    'DISPATCH_MAX_TARIFF_BONUS_SECONDS',
    '{"type": "object", "required": ["__default__"], "additionalProperties": {"type": "integer"}}'
),
(
    'DISPATCH_MIN_NEGATIVE_BONUS_SECONDS',
    '{"type": "integer", "maximum": 0}'
),
(
    'DISPATCH_REPOSITION_BONUS',
    '{"type": "object", "required": ["__default__"], "additionalProperties": {"type": "integer"}}'
),
(
    'DYNAMIC_DISTANCE_A',
    '{"type": "number"}'
),
(
    'DYNAMIC_DISTANCE_B',
    '{"type": "number"}'
),
(
    'DYNAMIC_TIME_A',
    '{"type": "number"}'
),
(
    'DYNAMIC_TIME_B',
    '{"type": "number"}'
),
(
    'E_ETA',
    '{"type": "number"}'
),
(
    'E_ETR',
    '{"type": "number"}'
),
(
    'K_ETR',
    '{"type": "number", "minimum": 0.0, "maximum": 1.0}'
),
(
    'MAX_ROBOT_DISTANCE',
    '{"type": "integer", "minimum": 1}'
),
(
    'MAX_ROBOT_TIME',
    '{"type": "integer", "minimum": 1}'
),
(
    'MAX_ROBOT_TIME_SCORE_ENABLED',
    '{"type": "boolean"}'
),
(
    'MAX_ROBOT_TIME_SCORE',
    '{"type": "integer", "minimum": 1}'
),
(
    'MIN_URGENCY',
    '{"type": "integer"}'
),
(
    'NEW_DRIVER_BONUS_DURATION_DAYS_P1',
    '{"type": "integer", "minimum": 0}'
),
(
    'NEW_DRIVER_BONUS_DURATION_DAYS_P2',
    '{"type": "integer", "minimum": 0}'
),
(
    'NEW_DRIVER_BONUS_VALUE_SECONDS',
    '{"type": "integer"}'
),
(
    'SURGES_RATIO_BONUS_ENABLED',
    '{"type": "boolean"}'
),
(
    'SURGES_RATIO_MAX_BONUS',
    '{"type": "integer", "minimum": 0}'
),
(
    'SURGES_RATIO_MIN_BONUS',
    '{"type": "integer", "maximum": 0}'
),
(
    'SURGES_RATIO_BONUS_COEFF',
    '{"type": "number", "minimum": 0}'
),
(
    'SURGE_BONUS_COEF',
    '{"type": "integer"}'
),
(
    'WAVE_THICKNESS_MINUTES',
    '{"type": "integer"}'
),
(
    'WAVE_THICKNESS_SECONDS',
    '{"type": "integer"}'
),
(
    'QUERY_LIMIT_FREE_PREFERRED',
    '{"type": "integer", "minimum": 1}'
),
(
    'QUERY_LIMIT_LIMIT',
    '{"type": "integer", "minimum": 1}'
),
(
    'QUERY_LIMIT_MAX_LINE_DIST',
    '{"type": "integer", "minimum": 1}'
),
(
    'QUERY_LIMIT_CLASSES_PREFERRED',
    '{"type": "object", "additionalProperties": false, "required": ["has_classes", "has_not_classes", "preferred"], "properties": {"has_classes": {"type": "array", "items": {"type": "string"}}, "has_not_classes": {"type": "array", "items": {"type": "string"}}, "preferred": {"type": "integer", "minimum": 1}}}'
),
(
    'ORDER_CHAIN_MAX_LINE_DISTANCE',
    '{"type": "integer", "minimum": 1}'
),
(
    'ORDER_CHAIN_MAX_ROUTE_DISTANCE',
    '{"type": "integer", "minimum": 1}'
),
(
    'ORDER_CHAIN_MAX_ROUTE_TIME',
    '{"type": "integer", "minimum": 1}'
),
(
    'ORDER_CHAIN_MIN_TAXIMETER_VERSION',
    '{"type": "string"}'
),
(
    'ORDER_CHAIN_PAX_EXCHANGE_TIME',
    '{"type": "integer", "minimum": 1}'
),
-- INVALID_SCHEMA_SETTING
(
    'INVALID_SCHEMA_SETTING',
    '{"type": "integer", "minimum": "STRING_AS_INVALID_SCHEMA_VALUE"}'
);


INSERT INTO dispatch_settings.settings
    (tariff_id, zone_id, param_id, version, value)
VALUES
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'QUERY_LIMIT_LIMIT'),
    0,
    '22'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_2'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'QUERY_LIMIT_LIMIT'),
    0,
    '23'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_3'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'QUERY_LIMIT_LIMIT'),
    0,
    '24'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_3'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_3'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'QUERY_LIMIT_MAX_LINE_DIST'),
    0,
    '28'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_3'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_3'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'QUERY_LIMIT_LIMIT'),
    0,
    '29'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_2'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'QUERY_LIMIT_LIMIT'),
    0,
    '25'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'QUERY_LIMIT_MAX_LINE_DIST'),
    0,
    '27'
);
