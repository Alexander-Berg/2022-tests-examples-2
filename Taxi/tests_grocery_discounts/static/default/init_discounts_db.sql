BEGIN TRANSACTION;

SET CONSTRAINTS ALL DEFERRED;

INSERT INTO menu_grocery_discounts.countries (field_type, field_value)
VALUES
('All', NULL),
('Type', 'Russia'),
('Any', NULL);

INSERT INTO menu_grocery_discounts.cities (field_type, field_value)
VALUES
('All', NULL),
('Type', 'Moscow'),
('Any', NULL);

INSERT INTO menu_grocery_discounts.depots (field_type, field_value)
VALUES
('All', NULL),
('Type', 'Taganka'),
('Any', NULL);

INSERT INTO menu_grocery_discounts.groups (field_type, field_value)
VALUES
('All', NULL),
('Type', 'Sweets'),
('Type', 'Meat'),
('Type', 'Ready meals'),
('Any', NULL),
('Type', 'Wheels');

INSERT INTO menu_grocery_discounts.products (field_type, field_value)
VALUES
('All', NULL),
('Type', 'Mars max'),
('Type', 'Kitkat Duo'),
('Type', 'Kitkat'),
('Type', 'Rich'),
('Type', 'Whiskas'),
('Type', 'Diary'),
('Any', NULL);

INSERT INTO menu_grocery_discounts.groups_priority (group_id, priority)
VALUES
(2, 3),
(3, 2),
(4, 1);

/* insert data into match tree */

INSERT INTO
    menu_grocery_discounts.cities_in_countries
        (country_id, city_id)
VALUES 
    (1/*All*/, 1/*All*/),
    (2/*Russia*/, 1/*All*/),
    (2/*Russia*/, 2/*Moscow*/);

INSERT INTO
    menu_grocery_discounts.depots_in_cities
        (cities_in_countries_relation, depot_id)
VALUES
    (1/*All,All*/, 1/*All*/),
    (2/*Rus,All*/, 1/*All*/),
    (3/*Rus,Mos*/, 1/*All*/),
    (3/*Rus,Mos*/, 2/*Taganka*/);

INSERT INTO
    menu_grocery_discounts.groups_in_depots
        (depots_in_cities_relation, group_id)
VALUES
    (1, 1),
    (2, 1),
    (3, 1),
    (4, 1),
    (4, 2);

INSERT INTO
    menu_grocery_discounts.products_in_groups
        (groups_in_depots_relation, product_id)
VALUES
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 1),
    (4, 5),
    (5, 1);

INSERT INTO
    menu_grocery_discounts.intervals_in_products
        (products_in_groups_relation, from_ts, to_ts, discount_value, exclusions, discount_meta_info)
VALUES
    (1, '1971-01-01 00:00:00.000+00',  '1973-01-02 00:00:00.000+00','{
                    "is_cashback": false,
                    "description": "Testing",
                    "discount_type": "absolute",
                    "schedule": [{"schedule":
                {
                    "timezone": "LOCAL",
                    "intervals": [
                        {
                          "exclude": false,
                          "day": [ 2, 4, 6]
                        },
                        {
                            "exclude": false,
                            "daytime": [
                                {
                                    "from": "10:00:00",
                                    "to": "19:00:00"
                                }
                            ]
                        }
                    ]
                }
            ,
            "value": {"value": "10.0", "value_type": "absolute"}}]
}
', '{"country":[],"city":[],"depot":[],"group":[],"product":[]}', '{"draft_id":"123"}'),
    (2, '1971-01-01 00:00:00.000+00',  '1973-01-02 00:00:00.000+00','{
                    "is_cashback": false,
                    "description": "Testing",
                    "discount_type": "absolute",
                    "schedule": [{"schedule":
                {
                    "timezone": "LOCAL",
                    "intervals": [
                        {
                          "exclude": false,
                          "day": [ 2, 4, 6]
                        },
                        {
                            "exclude": false,
                            "daytime": [
                                {
                                    "from": "10:00:00",
                                    "to": "19:00:00"
                                }
                            ]
                        }
                    ]
                }
            ,
            "value": {"value": "10.0", "value_type": "absolute"}}]
}
', '{"country":[],"city":[],"depot":[],"group":[],"product":[]}', '{"draft_id":"123"}'),
    (3, '1970-01-01 00:00:00.000+00',  '1973-01-02 00:00:00.000+00','{
                    "is_cashback": false,
                    "description": "Testing",
                    "discount_type": "absolute",
                    "schedule": [{"schedule":
                {
                    "timezone": "LOCAL",
                    "intervals": [
                        {
                          "exclude": false,
                          "day": [ 2, 4, 6]
                        },
                        {
                            "exclude": false,
                            "daytime": [
                                {
                                    "from": "10:00:00",
                                    "to": "19:00:00"
                                }
                            ]
                        }
                    ]
                }
            ,
            "value": {"value": "10.0", "value_type": "absolute"}}]
}
', '{"country": [], "city": [], "depot": [], "product": [], "group": []}', '{"draft_id":"123"}'),
    (4, '1970-01-01 00:00:00.000+00',  '1973-01-02 00:00:00.000+00','{
                    "is_cashback": false,
                    "description": "Testing",
                    "discount_type": "absolute",
                    "schedule": [{"schedule":
                {
                    "timezone": "LOCAL",
                    "intervals": [
                        {
                          "exclude": false,
                          "day": [ 2, 4, 6]
                        },
                        {
                            "exclude": false,
                            "daytime": [
                                {
                                    "from": "10:00:00",
                                    "to": "19:00:00"
                                }
                            ]
                        }
                    ]
                }
            ,
            "value": {"value": "10.0", "value_type": "absolute"}}]
}
', '{"country":[],"city":[],"depot":[],"group":[],"product":[]}', '{"draft_id":"123"}'),
    (5, '1970-01-01 00:00:00.000+00',  '1973-01-02 00:00:00.000+00','{
                    "is_cashback": false,
                    "description": "Testing",
                    "discount_type": "absolute",
                    "schedule": [{"schedule":
                {
                    "timezone": "LOCAL",
                    "intervals": [
                        {
                          "exclude": false,
                          "day": [ 2, 4, 6]
                        },
                        {
                            "exclude": false,
                            "daytime": [
                                {
                                    "from": "10:00:00",
                                    "to": "19:00:00"
                                }
                            ]
                        }
                    ]
                }
            ,
            "value": {"value": "10.0", "value_type": "absolute"}}]
}
', '{"country":[],"city":[],"depot":[],"group":[],"product":[]}', '{"draft_id":"123"}'),
    (6, '1970-01-01 00:00:00.000+00',  '1973-01-02 00:00:00.000+00','{
                    "is_cashback": false,
                    "description": "Testing",
                    "discount_type": "absolute",
                    "schedule": [{"schedule":
                {
                    "timezone": "LOCAL",
                    "intervals": [
                        {
                          "exclude": false,
                          "day": [ 2, 4, 6]
                        },
                        {
                            "exclude": false,
                            "daytime": [
                                {
                                    "from": "10:00:00",
                                    "to": "19:00:00"
                                }
                            ]
                        }
                    ]
                }
            ,
            "value": {"value": "10.0", "value_type": "absolute"}}]
}
', '{"country":[],"city":[],"depot":[],"group":[],"product":[]}', '{"draft_id":"123"}');

INSERT INTO grocery_discounts.groups_orders (root_name, groups, updated_at)
VALUES
('root1', ARRAY['group1', 'group2']::text[], '2020-07-12 10:00:00.000+03'),
('root2', ARRAY['group3', 'group1']::text[], '2020-07-15 10:00:00.000+03'),
('root2', ARRAY['group1', 'group3']::text[], '2020-07-13 10:00:00.000+03');


COMMIT TRANSACTION;
