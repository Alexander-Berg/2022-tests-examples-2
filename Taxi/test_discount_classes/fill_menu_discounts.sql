INSERT INTO grocery_discounts.country (entity_value)
VALUES ('russia');

INSERT INTO grocery_discounts.city (entity_value)
VALUES ('spb');

INSERT INTO grocery_discounts.group (entity_value)
VALUES ('food');

INSERT INTO grocery_discounts.class (entity_value)
VALUES ('TestClass1'), ('TestClass2');

INSERT INTO grocery_discounts.active_period (entity_value)
VALUES ('[2020-01-01 10:00:00.000+00, 2020-02-10 18:00:00.000+00]');

INSERT INTO grocery_discounts.match_data (data_id, data, series_id)
VALUES (1, '{
    "active_with_surge": true,
    "description": "TestClass1",
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
    "description": "TestClass2",
    "values_with_schedules": [
        {
            "money_value": {
                "menu_value": {
                    "value_type": "absolute",
                    "value": "2.0"
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
'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::UUID),
       (3, '{
    "active_with_surge": true,
    "description": "No class",
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
'cccccccc-cccc-cccc-cccc-cccccccccccc'::UUID);

INSERT INTO grocery_discounts.classes_orders(id, classes, updated_at)
VALUES
(511, ARRAY['TestClass1', 'TestClass2', 'No class']::text[], '2020-07-18 10:00:00.000+03'),
(411, ARRAY['TestClass2', 'TestClass1', 'No class']::text[], '2020-07-15 10:00:00.000+03'),
(311, ARRAY['No class']::text[], '2020-07-12 10:00:00.000+03');

INSERT INTO grocery_discounts.meta_info
VALUES (1, '{"create_draft_id":"unknown"}');

INSERT INTO grocery_discounts.match_rules_menu_discounts
(country, city, depot, "group", product, active_period, class, experiment, __data_id, __meta_info_id)
VALUES (3, 1, 2, 3, 1, 2, 2, 2, 1, 1), (3, 1, 2, 3, 1, 2, 1, 2, 3, 1), (3, 1, 2, 3, 1, 2, 3, 2, 2, 1);

INSERT INTO grocery_discounts.excluded_city (data_id, entity_id)
VALUES (1, 3);

INSERT INTO menu_grocery_discounts.groups (field_type, field_value)
VALUES ('Type', 'food');

INSERT INTO menu_grocery_discounts.groups_priority (group_id, priority)
VALUES (1, 1);
