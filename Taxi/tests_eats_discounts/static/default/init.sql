INSERT INTO eats_discounts.match_hierarchy(hierarchy_id, name)
VALUES ( 1, 'menu_discounts'),
       ( 2, 'cart_discounts'),
       ( 3, 'payment_method_discounts'),
       ( 4, 'place_cashback'),
       ( 5, 'place_menu_cashback'),
       ( 6, 'yandex_cashback'),
       ( 7, 'yandex_menu_cashback');

INSERT INTO eats_discounts.region (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.brand (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.place (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.payment_method (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.bins (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.product (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.product_set (entity_value)
VALUES (ARRAY[]::TEXT[]);

INSERT INTO eats_discounts.active_period (entity_value)
VALUES ('[1970-01-01 00:00:00.000+00, 2200-01-01 00:00:00.000+00]');

INSERT INTO eats_discounts.country (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.brand_orders_count (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.orders_count (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.place_orders_count (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.place_business (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.retail_orders_count (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.restaurant_orders_count (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.place_cashback_days (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.has_yaplus (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.place_has_yaplus (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.shipping_type (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.business_type (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.place_category (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.surge_range (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts."check" (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.yaplus_level (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.delivery_method (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.time_from_last_order_range (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.brand_time_from_last_order_range (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.place_time_from_last_order_range (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.class (entity_value)
VALUES ('default');

INSERT INTO eats_discounts.tag (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO eats_discounts.experiment (entity_type)
VALUES ('Other'), ('Any');

ALTER SEQUENCE eats_discounts.match_data_data_id_seq RESTART WITH 123;
ALTER SEQUENCE eats_discounts.match_rules_revision RESTART WITH 22;
