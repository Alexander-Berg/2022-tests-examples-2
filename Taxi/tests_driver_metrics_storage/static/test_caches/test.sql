INSERT INTO common.udids (udid_id,udid,master_udid_id)VALUES
(1001,'100000000000000000000000',NULL),
(1002,'200000000000000000000000',NULL),
(1003,'300000000000000000000000',1001),
(1004,'400000000000000000000000',1001),
(1005,'500000000000000000000000',1001),
(1006,'600000000000000000000000',1001);
INSERT INTO common.event_types (event_type_id,event_type)VALUES(1,'type-X');

CREATE SEQUENCE events_logs_event_id_test_seq;
INSERT INTO events.queue_64 (event_id,udid_id,event_type_id,created,deadline)
(select nextval('events_logs_event_id_test_seq'),1001,1,t,'2999-01-01T00:00:00+0000' from(
SELECT generate_series('2000-01-01T00:00:00'::TIMESTAMP, '2000-12-31T00:00:00'::TIMESTAMP, '1 day') t) p);
DROP SEQUENCE events_logs_event_id_test_seq;

INSERT INTO data.logs_64_partitioned (event_id,udid_id,created,loyalty_increment,activity_increment)
(SELECT event_id,udid_id,created,0,0 FROM events.logs_64_partitioned);
