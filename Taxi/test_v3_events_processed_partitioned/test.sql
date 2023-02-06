INSERT INTO events.logs_64_partitioned (event_id,udid_id,event_type_id,tariff_zone_id,created,deadline,order_id,order_alias,processed,dbid_uuid_id) VALUES
(1,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','order_alias','2100-01-01T00:00:00',1),
(2,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','order_alias','2100-01-01T00:00:00',1),
(3,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','order_alias','2100-01-01T00:00:00',1),
(4,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','order_alias','2100-01-01T00:00:00',1),
(5,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','order_alias','2100-01-01T00:00:00',1),
(6,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','order_alias','2100-01-01T00:00:00',1),
(7,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','order_alias','2100-01-01T00:00:00',1),
(8,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','order_alias','2100-01-01T00:00:00',1),
(9,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','order_alias','2100-01-01T00:00:00',1);

INSERT INTO data.logs_64_partitioned (event_id,udid_id,created,loyalty_increment,activity_increment) VALUES
(1,1001,'2100-01-01T00:00:00',NULL,NULL),
(2,1001,'2100-01-01T00:00:00',111, NULL),
(3,1001,'2100-01-01T00:00:00',NULL,222),
(4,1001,'2100-01-01T00:00:00',333,444);

INSERT INTO data.logs_64_partitioned (event_id,udid_id,created,loyalty_increment,activity_increment) VALUES
(5,1001,'2100-01-01T00:00:00',NULL,NULL),
(6,1001,'2100-01-01T00:00:00',666, NULL),
(7,1001,'2100-01-01T00:00:00',NULL,777),
(8,1001,'2100-01-01T00:00:00',888,999);
