INSERT INTO grocery_discounts.country (entity_value)
VALUES ('russia');

INSERT INTO grocery_discounts.city (entity_value)
VALUES ('spb');

INSERT INTO grocery_discounts.group (entity_value)
VALUES ('food');

INSERT INTO grocery_discounts.active_period (entity_value)
VALUES ('[2020-01-01 10:00:00.000+00, 2020-02-10 18:00:00.000+00]');

INSERT INTO grocery_discounts.match_data (data_id, data, series_id)
VALUES (1,
        '{
    "active_with_surge": true,
    "description": "Test",
    "values_with_schedules": [
        {
            "money_value": {
                "menu_value": {
                    "value_type": "absolute",
                    "value": "1.0"
                },
                "cart_value": {
                    "discount_values": {
                        "value_type": "table",
                        "value": [
                            {
                                "discount": {
                                    "value_type": "fraction",
                                    "value": "10.0"
                                },
                                "from_cost": "120.0"
                            }
                        ]
                    },
                    "maximum_discount": "10000.0"
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
'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::UUID);

INSERT INTO grocery_discounts.meta_info
VALUES (1, '{"create_draft_id": "grocery_draft_id_test", "create_multidraft_id": "create_multidraft_id", "create_author": "create_author"}');

INSERT INTO grocery_discounts.match_rules_menu_discounts
(country, city, depot, "group", product, active_period, __data_id, __meta_info_id)
VALUES (3, 1, 2, 3, 1, 2, 1, 1);

INSERT INTO grocery_discounts.excluded_city (data_id, entity_id)
VALUES (1, 3);
