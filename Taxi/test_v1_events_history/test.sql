-- include common.sql

INSERT INTO events.queue_64 (unique_rider_id,event_type_id,tariff_zone_id,created,deadline,order_id)VALUES
(1001,1,1,'2000-01-01T00:00:00','2100-01-01T00:00:00','order_id'),
(1001,2,2,'2000-01-01T00:10:00','2100-01-01T00:00:00',NULL),
(1001,1,NULL,'2000-01-01T00:20:00','2100-01-01T00:00:00',NULL),
(1001,1,NULL,'2000-01-01T00:30:00','2100-01-01T00:00:00',NULL),
(1003,3,NULL,'2000-01-01T00:40:00','2100-01-01T00:00:00',NULL),
(1004,2,1,'2000-01-01T00:00:50','2100-01-01T00:00:00',NULL),
(1005,1,2,'2000-01-01T00:01:00','2100-01-01T00:00:00',NULL),
(1006,1,NULL,'2000-01-01T00:01:10','2100-01-01T00:00:00',NULL),
(1002,2,2,'2000-01-01T00:10:00','2100-01-01T00:00:00','order_id2');

WITH del as (DELETE FROM events.queue RETURNING *)
INSERT INTO events.logs_64 (
	event_id, unique_rider_id, event_type_id, --
	tariff_zone_id, created, deadline, order_id, processed
) SELECT d.event_id, d.unique_rider_id, d.event_type_id, --
	 d.tariff_zone_id, d.created, d.deadline, d.order_id, d.created
FROM del as d;

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

INSERT INTO events.tickets_64 (unique_rider_id,down_counter,deadline)VALUES
(1001,4,'2100-01-01T00:00:00');