INSERT INTO events.queue_64 (event_id,udid_id,event_type_id,tariff_zone_id,created,deadline,order_id,activation,extra_data,descriptor) VALUES
(1,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','2000-01-01T00:00:00',NULL,NULL),
(2,1002,2,2,'2000-01-01T00:10:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00',NULL,'{"tags": ["yam-yam", "tas_teful"],"type": "user_test"}'),
(3,1003,1,NULL,'2000-01-01T00:20:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','{"extra_test":"extra_test"}',NULL),
(4,1004,2,2,'2000-01-01T00:40:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','{"extra_test":"extra_test"}','{"tags": ["yam-yam", "tas_teful"],"type": "user_test"}');
