INSERT INTO dispatch_settings.zones (zone_name) VALUES ('__default__'), ('zone1'), ('zone2');


INSERT INTO dispatch_settings.groups (name, description) VALUES ('group1', 'description');
INSERT INTO dispatch_settings.groups (name, description) VALUES ('group2', 'description');
INSERT INTO dispatch_settings.tariffs (tariff_name, group_id) VALUES
  ('__default__group1__', (SELECT id FROM dispatch_settings.groups WHERE name = 'group1')),
  ('test_tariff_1', (SELECT id FROM dispatch_settings.groups WHERE name = 'group1')),
  ('test_tariff_2', (SELECT id FROM dispatch_settings.groups WHERE name = 'group1')),
  ('__default__group2__', (SELECT id FROM dispatch_settings.groups WHERE name = 'group2'));

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
     WHERE tariff_name = '__default__group1__'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = '__default__'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    0,
    '22'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = '__default__'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'NEW_INTEGER_FIELD'),
    0,
    '22'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = '__default__group1__'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'zone1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'NEW_INTEGER_FIELD'),
    0,
    '22'
);
