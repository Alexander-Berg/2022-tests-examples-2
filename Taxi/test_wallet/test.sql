INSERT INTO common.udids (udid_id,master_udid_id,udid)VALUES
(1,NULL,'Q'),
(2,NULL,'W'),
(3,NULL,'E'),
(4,1,'Q.1'),
(5,1,'Q.2'),
(6,1,'Q.3');

INSERT INTO common.event_types (event_type_id,event_type)VALUES
(1,'QQQ');

INSERT INTO common.tariff_zones (tariff_zone_id,tariff_zone)VALUES
(1,'ZZZ');

INSERT INTO events.logs_64_partitioned (event_id,udid_id,event_type_id,created,tariff_zone_id,processed,deadline)VALUES
(1,1,1,'2000-01-01T00:00:00',NULL,'2000-01-01T00:00:00','2999-01-01T00:00:00+0000'),
(2,1,1,'2000-01-01T00:00:00',1,'2000-01-01T00:00:00','2999-01-01T00:00:00+0000');

INSERT INTO data.logs_64_partitioned (event_id,udid_id,created,loyalty_increment,activity_increment)VALUES
(1,1,'2000-01-01T00:00:01',10,NULL),
(2,1,'2000-01-01T00:00:01',10,NULL),
(11,1,'2000-01-01T00:00:02',NULL,11),
(22,1,'2000-01-01T00:00:02',NULL,11),
(23,6,'2000-01-01T00:00:02',6,11);
