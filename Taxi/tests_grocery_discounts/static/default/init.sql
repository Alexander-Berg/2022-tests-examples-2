INSERT INTO grocery_discounts.match_hierarchy(hierarchy_id, name)
VALUES (1, 'menu_discounts'),
       (2, 'cart_discounts'),
       (3, 'payment_method_discounts'),
       (4, 'dynamic_discounts'),
       (5, 'markdown_discounts'),
       (6, 'suppliers_discounts');

INSERT INTO grocery_discounts.class (entity_value)
VALUES ('No class');

INSERT INTO grocery_discounts.experiment (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_discounts.application_name (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO grocery_discounts.country (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_discounts.city (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_discounts.depot (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_discounts.payment_method (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_discounts.bins (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_discounts.group (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_discounts.product (entity_type)
VALUES ('Any'), ('Other');

INSERT INTO grocery_discounts.product_set (entity_value)
VALUES (ARRAY[]::TEXT[]);

INSERT INTO grocery_discounts.active_period (entity_value)
VALUES ('[2000-01-01 00:00:00.000+00, 2100-01-01 00:00:00.000+00]');

INSERT INTO grocery_discounts.label (entity_value)
VALUES ('default');

INSERT INTO grocery_discounts.tag (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO grocery_discounts.has_yaplus (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO grocery_discounts.orders_restriction (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO grocery_discounts.active_with_surge (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO grocery_discounts.master_group (entity_type)
VALUES ('Other'), ('Any');

ALTER SEQUENCE grocery_discounts.match_rules_revision RESTART WITH 1234;
ALTER SEQUENCE grocery_discounts.match_data_data_id_seq RESTART WITH 123;
