INSERT INTO events.queue_64 (event_id,udid_id,event_type_id,tariff_zone_id,created,deadline,order_id,activation,extra_data,descriptor) VALUES
(300000000001,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','2000-01-01T00:00:00',NULL,NULL),
(300000000002,1002,2,2,'2000-01-01T00:10:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00',NULL,'{"tags": ["yam-yam", "tas_teful"],"type": "user_test"}'),
(300000000003,1003,1,NULL,'2000-01-01T00:20:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','{"extra_test":"extra_test"}',NULL),
(300000000005,1005,2,2,'2000-01-01T00:40:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','{"extra_test":"extra_test"}','{"tags": ["yam-yam", "tas_teful"],"type": "user_test"}'),
(300000000006,1006,1,NULL,'2000-01-01T00:50:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','{"extra_test":"extra_test"}','{"tags": ["yam-yam", "tas_teful"],"type": "user_test"}');

-- Events with parsing extra_data and descriptor with errors
INSERT INTO events.queue_64 (event_id,udid_id,event_type_id,tariff_zone_id,created,deadline,order_id,activation,extra_data,descriptor) VALUES
(300000000007,1001,2,2,'2000-01-01T00:10:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00',NULL,'{"tags": "yam-yam", "tas_teful"],"type": "user_test"}'),
(300000000008,1002,1,NULL,'2000-01-01T00:20:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','{"extra_test":"extra_test"',NULL),
(300000000012,1006,2,2,'2000-01-01T00:40:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','{"extra_test":"extra_test"','{"tagsphy": ["yam-yam", "tas_teful"],"typem": "user_test"}');
