INSERT INTO grocery_discounts.country (entity_value)
VALUES ('RUS');

INSERT INTO grocery_discounts.city (entity_value)
VALUES ('213'),('2');

INSERT INTO grocery_discounts.depot (entity_value)
VALUES ('999999');

INSERT INTO grocery_discounts.group (entity_value)
VALUES ('food'), ('misc'), ('excluded_group');

INSERT INTO grocery_discounts.product (entity_value)
VALUES ('3'), ('4'), ('5'), ('6'), ('excluded_product');

INSERT INTO grocery_discounts.experiment (entity_value)
VALUES ('first'), ('second');

INSERT INTO grocery_discounts.active_period (entity_value)
VALUES ('[2020-01-01 09:00:01.000+00, 2021-01-01 00:00:00.000+00]');

INSERT INTO grocery_discounts.match_data (data_id, data, series_id)
VALUES (1, '{
    "active_with_surge": true,
    "description": "TestExperiment1",
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
    "description": "TestExperiment2",
    "values_with_schedules": [
        {
            "money_value": {
                "menu_value": {
                    "value_type": "absolute",
                    "value": "2.0"
                }
            },
            "cashback_value": {
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
     "discount_meta" : {
        "is_price_strikethrough" : true,
        "is_expiring": true
     },
    "description": "TestExperiment3",
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
'cccccccc-cccc-cccc-cccc-cccccccccccc'::UUID),
       (4, '{
    "active_with_surge": true,
     "discount_meta" : {
        "is_price_strikethrough" : true,
        "is_expiring": true
     },
    "description": "TestExperiment3",
    "values_with_schedules": [
        {
            "money_value": {"menu_value": {"value_type": "absolute", "value": "1.5"}},
            "schedule": {
                "timezone": "LOCAL",
                "intervals": [
                    {"exclude": false, "day": [1, 2, 3, 4, 5, 6, 7]}
                ]
            }
        }
    ]
}',
'dddddddd-dddd-dddd-dddd-dddddddddddd'::UUID);


INSERT INTO grocery_discounts.meta_info
VALUES (1, '{"create_draft_id":"unknown"}');

INSERT INTO grocery_discounts.match_rules_menu_discounts
(country, city, tag, depot, "group", product, active_period, class, experiment, __data_id, __meta_info_id)
VALUES (3, 3, 1, 1, 3, 1, 2, 1, 1, 2, 1), (3, 1, 1, 3, 3, 2, 2, 1, 1, 1, 1),
       (3, 1, 1, 1, 3, 3, 2, 1, 2, 1, 1), (3, 1, 1, 2, 3, 4, 2, 1, 3, 2, 1),
       (3, 1, 1, 2, 3, 4, 2, 1, 4, 2, 1), (3, 1, 1, 2, 3, 4, 2, 1, 2, 4, 1),
       (3, 1, 1, 2, 3, 5, 2, 1, 1, 1, 1), (3, 1, 1, 2, 3, 1, 2, 1, 1, 3, 1);

INSERT INTO grocery_discounts.excluded_product (data_id, entity_id)
VALUES (3, 7);

INSERT INTO menu_grocery_discounts.groups (field_type, field_value)
VALUES ('Type', 'food'), ('Type', 'misc');

INSERT INTO menu_grocery_discounts.groups_priority (group_id, priority)
VALUES (1, 1), (2, 2);

INSERT INTO grocery_discounts.experiments_orders(id, experiments, updated_at)
VALUES
(511, ARRAY['first', 'second']::text[], '2020-01-08 10:00:00.000+03');
