INSERT INTO grocery_discounts.country (entity_value)
VALUES ('RUS'), ('usa');

INSERT INTO grocery_discounts.city (entity_value)
VALUES ('213'), ('voronezh');

INSERT INTO grocery_discounts.group (entity_value)
VALUES ('food');

INSERT INTO grocery_discounts.depot (entity_value)
VALUES ('mega');

INSERT INTO grocery_discounts.experiment (entity_value)
VALUES ('testExp1');

INSERT INTO grocery_discounts.active_period (entity_value, is_start_utc, is_end_utc)
VALUES ('[2020-01-01 10:00:00.000+00, 2020-02-10 18:00:00.000+00]', false, false),
       ('[2020-02-13 10:00:00.000+00, 2020-02-13 12:00:00.000+00]', true, true),
       ('[2020-02-13 10:00:00.000+00, 2020-02-13 12:00:00.000+00]', false, false);

INSERT INTO grocery_discounts.match_data (data_id, data, series_id)
VALUES (1, '{
    "active_with_surge": true,
    "description": "Test",
    "values_with_schedules": [
        {
            "money_value": {
                "menu_value": {
                    "value_type": "absolute",
                    "value": "1.0"
                }
            },
            "schedule": {
                "timezone": "LOCAL",
                "intervals": [
                    {"exclude": false, "day": [1, 2, 3, 4, 5, 6, 7]}
                ]
            }
        }
    ]
}',
'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::UUID),
(2, '{
    "active_with_surge": true,
    "description": "Test",
    "values_with_schedules": [
        {
            "money_value": {
                "menu_value": {
                    "value_type": "absolute",
                    "value": "3.0"
                }
            },
            "schedule": {
                "timezone": "LOCAL",
                "intervals": [
                    {"exclude": false, "day": [1, 2, 3, 4, 5, 6, 7]}
                ]
            }
        }
    ]
}',
'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::UUID);

INSERT INTO grocery_discounts.meta_info
VALUES (1, '{"create_draft_id":"unknown"}');

INSERT INTO grocery_discounts.match_rules_menu_discounts
(country, city, depot, "group", product, active_period, class, experiment, __data_id, __meta_info_id)
VALUES (3, 1, 1, 3, 1, 2, 1, 3, 1, 1),
       (3, 3, 2, 1, 1, 2, 1, 3, 1, 1),
       (3, 1, 3, 2, 1, 2, 1, 3, 1, 1),
       (3, 3, 3, 2, 1, 3, 1, 3, 1, 1),
       (3, 3, 3, 2, 1, 4, 1, 3, 1, 1),
       (4, 4, 2, 2, 1, 2, 1, 3, 1, 1);

INSERT INTO menu_grocery_discounts.groups (field_type, field_value)
VALUES ('Type', 'food');

INSERT INTO menu_grocery_discounts.groups_priority (group_id, priority)
VALUES (1, 1);