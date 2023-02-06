INSERT INTO common.udids (udid_id,udid,master_udid_id)VALUES
(1001,'100000000000000000000000',NULL),
(1002,'200000000000000000000000',NULL),
(1003,'300000000000000000000000',1001),
(1004,'400000000000000000000000',1001),
(1005,'500000000000000000000000',1001),
(1006,'600000000000000000000000',1001);
INSERT INTO common.event_types (event_type)VALUES
('type-X'),('type-Y'),('type-Z');
INSERT INTO common.tariff_zones (tariff_zone)VALUES
('moscow'),('spb');
INSERT INTO common.dbid_uuids (dbid_uuid)VALUES
('dbid_uuid1'),('dbid_uuid2');
INSERT INTO data.activity_values (udid_id,value,updated)VALUES
(1002,222,'2000-01-01T00:00:00'),
(1004,444,'2000-01-01T00:00:00');

INSERT INTO events.queue_64 (udid_id,dbid_uuid_id,event_type_id,tariff_zone_id,created,deadline,order_id,order_alias)VALUES
(1001,1,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id',NULL),
(1001,1,2,2,'2000-01-01T00:10:00','2100-01-01T00:00:00',NULL,'order_alias'),
(1001,1,1,NULL,'2000-01-01T00:20:00','2100-01-01T00:00:00',NULL,NULL),
(1001,1,1,NULL,'2000-01-01T00:30:00','2100-01-01T00:00:00',NULL,NULL),
(1003,1,3,NULL,'2000-01-01T00:40:00','2100-01-01T00:00:00',NULL,NULL),
(1004,2,2,1,'2000-01-01T00:00:50','2100-01-01T00:00:00',NULL,NULL),
(1005,2,1,2,'2000-01-01T00:01:00','2100-01-01T00:00:00',NULL,NULL),
(1006,2,1,NULL,'2000-01-01T00:01:10','2100-01-01T00:00:00',NULL,NULL),
(1002,2,2,2,'2000-01-01T00:10:00','2100-01-01T00:00:00','order_id2',NULL);

INSERT INTO events.tokens (token,deadline)VALUES
('eid-1','2100-01-01T00:00:00'),
('eid-2','2100-01-01T00:00:00'),
('eid-3','2100-01-01T00:00:00'),
('eid-4','2100-01-01T00:00:00'),
('eid-5','2100-01-01T00:00:00'),
('eid-6','2100-01-01T00:00:00'),
('eid-7','2100-01-01T00:00:00'),
('eid-8','2100-01-01T00:00:00'),
('eid-9','2100-01-01T00:00:00');

INSERT INTO events.tickets_64 (udid_id,down_counter,deadline)VALUES
(1001,4,'2100-01-01T00:00:00');
