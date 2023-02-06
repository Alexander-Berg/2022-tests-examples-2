INSERT INTO grocery_marketing.match_hierarchy(name)
VALUES (/*1*/'menu_tags');

INSERT INTO grocery_marketing.country (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_marketing.city (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_marketing.depot (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_marketing.group (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_marketing.product (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_marketing.rule_id (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_marketing.active_period (entity_value)
VALUES ('[2000-01-01 00:00:00.000+00, 2100-01-01 00:00:00.000+00]');
