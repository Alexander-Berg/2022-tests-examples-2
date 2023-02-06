INSERT INTO common.udids (udid,master_udid_id)VALUES
('100000000000000000000000',NULL),('W',NULL),('E',1),('R',1),('T',1),('Y',1);
INSERT INTO common.event_types (event_type)VALUES
('type-X'),('type-Y'),('type-Z');
INSERT INTO common.tariff_zones (tariff_zone)VALUES
('moscow'),('spb');
INSERT INTO data.activity_values (udid_id,value,updated)VALUES
(2,222,'2000-01-01T00:00:00'),(4,444,'2000-01-01T00:00:00');

INSERT INTO events.queue_64 (udid_id,event_type_id,tariff_zone_id,created,deadline,order_id,order_alias,activation)VALUES
(1,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id',NULL,'2000-01-01T00:00:00'),
(1,2,2,'2000-01-01T00:10:00','2100-01-01T00:00:00',NULL,'order_alias','2000-01-01T00:00:00'),
(1,1,NULL,'2000-01-01T00:20:00','2100-01-01T00:00:00',NULL,NULL,'2000-01-01T00:00:00'),
(1,1,NULL,'2000-01-01T00:30:00','2100-01-01T00:00:00',NULL,NULL,'2000-01-01T00:00:00'),
(3,3,NULL,'2000-01-01T00:40:00','2100-01-01T00:00:00',NULL,NULL,'2000-01-01T00:00:00'),
(4,2,1,'2000-01-01T00:00:50','2100-01-01T00:00:00',NULL,NULL,'2000-01-01T00:00:00'),
(5,1,2,'2000-01-01T00:01:00','2100-01-01T00:00:00',NULL,NULL,'2000-01-01T00:00:00'),
(6,1,NULL,'2000-01-01T00:01:10','2100-01-01T00:00:00',NULL,NULL,'2000-01-01T00:00:00'),
(2,2,2,'2000-01-01T00:10:00','2100-01-01T00:00:00',NULL,NULL,'2000-01-01T00:00:00');

WITH move AS (
	DELETE FROM events.queue_64
	RETURNING event_id,udid_id,event_type_id,tariff_zone_id,created,deadline,order_id,order_alias
)
INSERT INTO events.logs_64_partitioned (event_id,udid_id,event_type_id,tariff_zone_id,created,processed,deadline,order_id,order_alias)
	SELECT event_id,udid_id,event_type_id,tariff_zone_id,created,'2000-01-01T00:00:00',deadline,order_id,order_alias FROM move;
