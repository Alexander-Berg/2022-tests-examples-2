INSERT INTO dispatch_settings.zones (zone_name) VALUES ('__default__');

INSERT INTO dispatch_settings.groups (name, description) VALUES ('old', 'description');

INSERT INTO dispatch_settings.tariffs (tariff_name, group_id) VALUES ('__default__old__', (SELECT id FROM dispatch_settings.groups WHERE name = 'old'));

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
     WHERE tariff_name = '__default__old__'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = '__default__'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
    10,
    '22'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = '__default__old__'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = '__default__'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'NEW_INTEGER_FIELD'),
    11,
    '3'
);
