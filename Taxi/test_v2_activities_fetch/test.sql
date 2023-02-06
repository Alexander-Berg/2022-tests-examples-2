INSERT INTO common.udids (udid_id,udid,master_udid_id)VALUES
(1001,'Q00000000000000000000000',NULL),
(1002,'W00000000000000000000000',NULL),
(1003,'E00000000000000000000000',1001),
(1004,'R00000000000000000000000',1001),
(1005,'T00000000000000000000000',1001),
(1006,'Y00000000000000000000000',1001);
INSERT INTO common.event_types (event_type)VALUES('type-X'),('type-Y'),('type-Z');
INSERT INTO common.tariff_zones (tariff_zone)VALUES('moscow'),('spb');

INSERT INTO data.activity_values (udid_id,value,updated)VALUES
(1002,222,'2000-01-01T00:00:00'),
(1004,444,'2000-01-01T00:00:00');

INSERT INTO data.activity_values_generations (udid_id,generation)VALUES
(1002,nextval('data.activity_values_generation_sequence')),
(1004,0),
(1004,NULL);

INSERT INTO events.queue_64 (event_id,udid_id,event_type_id,created,deadline,activation)
(SELECT id,1001+(id-1)%3,1,dt,'2050-01-01T00:00:00',dt
FROM(
SELECT
generate_series(1, 10, 1) id,
generate_series('2000-01-01T00:00:00'::TIMESTAMP, '2000-01-10T00:00:00'::TIMESTAMP, '1 day') dt
) p);
