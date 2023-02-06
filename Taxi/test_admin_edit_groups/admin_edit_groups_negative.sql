INSERT INTO dispatch_settings.groups (name, description) VALUES ('group1', 'description_1');

INSERT INTO dispatch_settings.groups (name, description) VALUES ('group2', 'description_2');
INSERT INTO dispatch_settings.tariffs (tariff_name, group_id) VALUES ('__default__group2__', (SELECT id FROM dispatch_settings.groups WHERE name = 'group2'));
INSERT INTO dispatch_settings.tariffs (tariff_name, group_id) VALUES ('new_tariff_1', (SELECT id FROM dispatch_settings.groups WHERE name = 'group2'));
INSERT INTO dispatch_settings.tariffs (tariff_name, group_id) VALUES ('new_tariff_2', (SELECT id FROM dispatch_settings.groups WHERE name = 'group2'));

INSERT INTO dispatch_settings.groups (name, description) VALUES ('group3', 'description_3');
INSERT INTO dispatch_settings.tariffs (tariff_name, group_id) VALUES ('__default__group3__', (SELECT id FROM dispatch_settings.groups WHERE name = 'group3'));
INSERT INTO dispatch_settings.tariffs (tariff_name, group_id) VALUES ('new_tariff_3', (SELECT id FROM dispatch_settings.groups WHERE name = 'group3'));
INSERT INTO dispatch_settings.tariffs (tariff_name, group_id) VALUES ('new_tariff_4', (SELECT id FROM dispatch_settings.groups WHERE name = 'group3'));

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
