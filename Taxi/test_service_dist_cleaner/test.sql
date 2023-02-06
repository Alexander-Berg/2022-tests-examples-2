-- include common.sql

-- records for testcase
INSERT INTO events.tokens (token,deadline)VALUES
('eid-3','2100-01-01T00:00:00'),
('eid-4','2100-01-01T00:00:00');

INSERT INTO events.logs_64_partitioned (event_id,unique_rider_id,event_type_id,tariff_zone_id,created,deadline,processed,order_id)VALUES
(3,1003,1,NULL,'2000-01-01T00:20:00','2100-01-01T00:00:00','2000-01-01T00:21:00',NULL),
(4,1004,1,NULL,'2000-01-01T00:30:00','2100-01-01T00:00:00','2000-01-01T00:31:00',NULL);

INSERT INTO events.tickets_64 (unique_rider_id,down_counter,deadline)VALUES
(1003,4,'2100-01-01T00:00:00'),
(1004,4,'2100-01-01T00:00:00');
