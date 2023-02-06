INSERT INTO ride_discounts.zone (name, type, is_prioritized)
VALUES ('br_root', 'geonode', false);

INSERT INTO ride_discounts.tag_from_experiment (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO ride_discounts.tag (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO ride_discounts.payment_method (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO ride_discounts.bins (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO ride_discounts.application_brand (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO ride_discounts.application_platform (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO ride_discounts.application_type (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO ride_discounts.has_yaplus (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO ride_discounts.tariff (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO ride_discounts.active_period (entity_value, is_start_utc, is_end_utc)
VALUES ('[1970-01-01 00:00:00.000+00, 2200-01-01 00:00:00.000+00]', false, false);

INSERT INTO ride_discounts.order_type (entity_type)
VALUES ('Other'),
       ('Any');

INSERT INTO ride_discounts.class (entity_value)
VALUES ('default');

INSERT INTO ride_discounts.geoarea_a_set (entity_value)
VALUES (ARRAY[]::TEXT[]);

INSERT INTO ride_discounts.geoarea_b_set (entity_value)
VALUES (ARRAY[]::TEXT[]);

INSERT INTO ride_discounts.point_b_is_set (entity_type)
VALUES ('Other');

INSERT INTO ride_discounts.point_b_is_set (entity_value)
VALUES (0), (1);

INSERT INTO ride_discounts.surge_range (entity_type)
VALUES ('Other'), ('Any');

INSERT INTO ride_discounts.intermediate_point_is_set (entity_type, entity_value)
VALUES ('Other', NULL),
       ('Type' , 0   );

INSERT INTO ride_discounts.trips_restriction (entity_type)
VALUES ('Other'), ('Any');
