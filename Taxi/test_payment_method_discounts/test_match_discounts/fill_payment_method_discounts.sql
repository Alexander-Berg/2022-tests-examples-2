INSERT INTO grocery_discounts.country (entity_value)
VALUES ('russia');

INSERT INTO grocery_discounts.city (entity_value)
VALUES ('spb');

INSERT INTO grocery_discounts.bins (entity_value)
VALUES ('SuperGroup');

INSERT INTO grocery_discounts.group (entity_value)
VALUES ('food');

INSERT INTO grocery_discounts.application_name (entity_value)
VALUES ('android');

INSERT INTO grocery_discounts.payment_method (entity_value)
VALUES ('card');

INSERT INTO grocery_discounts.active_period (entity_value)
VALUES ('[2020-01-01 10:00:00.000+00, 2020-02-10 18:00:00.000+00]');

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
VALUES (1, '{"create_draft_id":"unknown"}');

INSERT INTO grocery_discounts.match_rules_payment_method_discounts
(country, city, depot, payment_method, application_name, bins, "group", product, active_period, experiment, __data_id, __meta_info_id)
VALUES (3, 1, 1, 2, 3, 3, 3, 1, 2, 2, 1, 1);

INSERT INTO grocery_discounts.excluded_city (data_id, entity_id)
VALUES (1, 3);

INSERT INTO grocery_discounts.excluded_payment_method (data_id, entity_id)
VALUES (1, 3);

INSERT INTO menu_grocery_discounts.groups (field_type, field_value)
VALUES ('Type', 'food');

INSERT INTO menu_grocery_discounts.groups_priority (group_id, priority)
VALUES (1, 1);

INSERT INTO grocery_discounts.bin_sets(id, bin_set_name, bins, from_ts, to_ts)
VALUES
(511, 'SuperGroup', '{123321, 405060}', '2020-01-01 05:00:00.000+03', '2020-07-18 10:00:00.000+03'),
(411, 'AlphaBank', '{444444, 555555}', '2020-01-01 05:00:00.000+03', '2020-08-12 10:00:00.000+03');

INSERT INTO grocery_discounts.bins_priority (bin_set_id, priority)
VALUES
(511, 1),
(411, 2);