INSERT INTO grocery_marketing.country (entity_value)
VALUES ('russia');

INSERT INTO grocery_marketing.city (entity_value)
VALUES ('spb');

INSERT INTO grocery_marketing.group (entity_value)
VALUES ('food');

INSERT INTO grocery_marketing.active_period (entity_value)
VALUES ('[2020-01-01 10:00:00.000+00, 2020-02-10 18:00:00.000+00]');

INSERT INTO grocery_marketing.match_data (data, series_id)
VALUES ('{
    "active_with_surge": true,
    "description": "Test",
    "values_with_schedules": [
        {
            "value": {"tag": "some_tag_2", "kind": "marketing"},
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

INSERT INTO grocery_marketing.meta_info
VALUES (1, '{"create_draft_id": "grocery_draft_id_test"}');

INSERT INTO grocery_marketing.match_rules_menu_tags
(country, city, depot, "group", product, active_period, __data_id, __meta_info_id)
VALUES (3, 1, 2, 3, 1, 2, 1, 1);

INSERT INTO grocery_marketing.excluded_city (data_id, entity_id)
VALUES (1, 3);
