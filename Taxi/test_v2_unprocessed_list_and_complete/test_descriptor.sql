INSERT INTO events.queue_64 (event_id,unique_rider_id,event_type_id,tariff_zone_id,created,deadline,order_id,activation,extra_data,descriptor) VALUES
(300000000001,1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id','2000-01-01T00:00:00',NULL,NULL),
(300000000002,1002,2,2,'2000-01-01T00:10:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00',NULL,'{"tags": ["yam-yam", "tas_teful"],"name": "user_test"}'),
(300000000003,1003,1,NULL,'2000-01-01T00:20:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','{"extra_test":"extra_test"}',NULL),
(300000000004,1004,2,2,'2000-01-01T00:40:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','{"extra_test":"extra_test"}','{"tags": ["yam-yam", "tas_teful"],"name": "user_test"}'),
(300000000005,1001,2,2,'2000-01-01T00:10:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00',NULL,'{"tagsqwer": ["yam-yam", "tas_teful"],"nameololo": "user_test"}');

-- Events with invalid extra_data or desciptor
INSERT INTO events.queue_64 (event_id,unique_rider_id,event_type_id,tariff_zone_id,created,deadline,order_id,activation,extra_data,descriptor) VALUES
(300000000006,1002,1,NULL,'2000-01-01T00:20:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','extra_test":"extra_test"}',NULL),
(300000000007,1003,2,2,'2000-01-01T00:40:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','{"extra_test"678---"extra_test"}','{"0000": ["yam-yam", "tas_teful"],"name": "user_test"}'),
(300000000008,1004,2,2,'2000-01-01T00:40:00','2100-01-01T00:00:00',NULL,'2000-01-01T00:00:00','{"extra_test":"extra_test"}','{"tags1": ["yam-yam", "tas_teful"],"name1": "user_test"}');
