INSERT INTO dispatch_settings.zones (zone_name)
VALUES ('__default__'),
       ('test_zone_1'),
       ('test_zone_2'),
       ('test_zone_3'),
       ('test_zone_4');

INSERT INTO dispatch_settings.groups (name, description) VALUES ('group1', 'description'), ('another_group', 'description');

INSERT INTO dispatch_settings.tariffs (tariff_name, group_id)
VALUES ('__default__group1__', (SELECT id FROM dispatch_settings.groups WHERE name = 'group1')),
       ('test_tariff_1', (SELECT id FROM dispatch_settings.groups WHERE name = 'group1')),
       ('test_tariff_2', (SELECT id FROM dispatch_settings.groups WHERE name = 'another_group')),
       ('test_tariff_3', NULL),
       ('test_tariff_4', (SELECT id FROM dispatch_settings.groups WHERE name = 'group1')),
       ('test_tariff_5', (SELECT id FROM dispatch_settings.groups WHERE name = 'group1')),
       ('test_tariff_6', NULL);

INSERT INTO dispatch_settings.parameters (field_name, schema)
VALUES
(
    'INTEGER_POSITIVE_FIELD',
    '{"type": "integer", "minimum": 0}'
),
(
    'REMOVABLE_FIELD',
    '{"type": "integer"}'
),
(
    'LIST_FIELD',
    '{"type": "array", "items": {"type": "string"}}'
),
(
    'DICT_FIELD',
    '{"type": "object", "required": ["__default__"], "additionalProperties": {"type": "integer"}}'
),
(
    'NEW_INTEGER_FIELD',
    '{"type": "integer"}'
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
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '22'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'REMOVABLE_FIELD'),
    0,
    '44'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'LIST_FIELD'),
    0,
    '["a1", "a2", "a3"]'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'DICT_FIELD'),
    0,
    '{"__default__": 33, "key1": 44}'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_2'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '22'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = '__default__group1__'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_3'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '222'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_3'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '1'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_2'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_3'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '2'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_3'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_3'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '3'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_4'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_3'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '4'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_5'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_3'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '5'
);

INSERT INTO dispatch_settings.actions (name)
VALUES ('set'),
       ('remove'),
       ('add_kv'),
       ('edit_kv'),
       ('add_items'),
       ('remove_items'),
       ('update_dict'),
       ('remove_kvs');

INSERT INTO dispatch_settings.allowed_actions(param_id, action_id)
VALUES
(
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    (SELECT id FROM dispatch_settings.actions
     WHERE name = 'set')
),
(
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'NEW_INTEGER_FIELD'),
    (SELECT id FROM dispatch_settings.actions
     WHERE name = 'set')
),
(
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    (SELECT id FROM dispatch_settings.actions
     WHERE name = 'remove')
),
(
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'REMOVABLE_FIELD'),
    (SELECT id FROM dispatch_settings.actions
     WHERE name = 'remove')
),
(
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'LIST_FIELD'),
    (SELECT id FROM dispatch_settings.actions
     WHERE name = 'set')
),
(
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'LIST_FIELD'),
    (SELECT id FROM dispatch_settings.actions
     WHERE name = 'add_items')
),
(
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'LIST_FIELD'),
    (SELECT id FROM dispatch_settings.actions
     WHERE name = 'remove_items')
),
(
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'DICT_FIELD'),
    (SELECT id FROM dispatch_settings.actions
     WHERE name = 'add_kv')
),
(
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'DICT_FIELD'),
    (SELECT id FROM dispatch_settings.actions
     WHERE name = 'edit_kv')
),
(
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'DICT_FIELD'),
    (SELECT id FROM dispatch_settings.actions
     WHERE name = 'update_dict')
),
(
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'DICT_FIELD'),
    (SELECT id FROM dispatch_settings.actions
     WHERE name = 'remove_kvs')
);

