INSERT INTO dispatch_settings.zones (zone_name)
VALUES ('__default__'),
       ('test_zone_1'),
       ('test_zone_2');

INSERT INTO dispatch_settings.tariffs (tariff_name)
VALUES ('test_tariff_1');

INSERT INTO dispatch_settings.parameters (field_name, schema)
VALUES
(
    'MAX_ROBOT_DISTANCE',
    '{"type": "integer", "minimum": 1}'
);


INSERT INTO dispatch_settings.settings (tariff_id, zone_id, param_id, version, value)
VALUES
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_1'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'MAX_ROBOT_DISTANCE'),
    1,
    '1'
),
(
    (SELECT id FROM dispatch_settings.tariffs
     WHERE tariff_name = 'test_tariff_1'),
    (SELECT id FROM dispatch_settings.zones
     WHERE zone_name = 'test_zone_2'),
    (SELECT id FROM dispatch_settings.parameters
     WHERE field_name = 'MAX_ROBOT_DISTANCE'),
    2,
    '2'
);
