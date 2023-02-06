INSERT INTO dispatch_settings.zones (zone_name)
VALUES ('__default__'),
       ('test_zone_1'),
       ('test_zone_2');

INSERT INTO dispatch_settings.groups (name, description) VALUES ('base', 'description');

INSERT INTO dispatch_settings.tariffs (tariff_name, group_id)
VALUES ('__default__base__', (SELECT id FROM dispatch_settings.groups WHERE name = 'base')),
       ('test_tariff_1', (SELECT id FROM dispatch_settings.groups WHERE name = 'base')),
       ('test_tariff_2', (SELECT id FROM dispatch_settings.groups WHERE name = 'base')),
       ('test_tariff_3', (SELECT id FROM dispatch_settings.groups WHERE name = 'base')),
       ('test_tariff_4', NULL);

INSERT INTO dispatch_settings.parameters (field_name, schema)
VALUES
(
    'MAX_ROBOT_TIME',
    '{"type": "integer", "minimum": 1}'
),
(
    'QUERY_LIMIT_LIMIT',
    '{"type": "integer", "minimum": 1}'
);


INSERT INTO dispatch_settings.settings
       (tariff_id, zone_id, param_id, version, value)
VALUES
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = '__default__base__'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'QUERY_LIMIT_LIMIT'),
    2,
    '2'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = '__default__base__'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'MAX_ROBOT_TIME'),
    3,
    '3'
),


(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'QUERY_LIMIT_LIMIT'),
    4,
    '4'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'MAX_ROBOT_TIME'),
    5,
    '5'
);
