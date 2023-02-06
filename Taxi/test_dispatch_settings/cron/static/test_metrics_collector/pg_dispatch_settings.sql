INSERT INTO dispatch_settings.zones (zone_name)
VALUES ('__default__'),
       ('test_zone_1'),
       ('test_zone_2'),
       ('test_zone_3'),
       ('test_zone_4'),
       ('test_zone_5');

INSERT INTO dispatch_settings.tariffs (tariff_name)
VALUES ('test_tariff_1'),
       ('test_tariff_2'),
       ('test_tariff_3'),
       ('test_tariff_4'),
       ('test_tariff_5'),
       ('__default__group1__'),
       ('__default__group2__');

INSERT INTO dispatch_settings.parameters (field_name, schema)
VALUES
(
    'INTEGER_POSITIVE_FIELD',
    '{"type": "integer", "minimum": 0}'
),
(
    'NEW_INTEGER_FIELD',
    '{"type": "integer"}'
);

INSERT INTO dispatch_settings.settings (tariff_id, zone_id, param_id, version, value)
VALUES
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = '__default__'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'NEW_INTEGER_FIELD'),
    0,
    '1'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = '__default__'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '2'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_2'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = '__default__'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'NEW_INTEGER_FIELD'),
    0,
    '3'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = '__default__group1__'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = '__default__'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '4'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = '__default__group1__'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = '__default__'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'NEW_INTEGER_FIELD'),
    0,
    '5'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '6'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_5'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    NULL
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = '__default__group1__'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_5'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    NULL
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = '__default__group1__'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_5'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'NEW_INTEGER_FIELD'),
    0,
    NULL
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_2'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_5'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '666'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_2'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_5'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'NEW_INTEGER_FIELD'),
    0,
    NULL
);

-- For fetch_settings_count.sqlt we need to analyze tables
ANALYZE;
