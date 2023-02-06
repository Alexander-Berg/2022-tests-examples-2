INSERT INTO common.udids (udid_id,udid)VALUES(1,'Q'),(2,'W'),(3,'E'),(4,'R'),(5,'T'),(6,'Y');
INSERT INTO common.event_types (event_type_id,event_type)VALUES(1,'type-X');

CREATE SEQUENCE events_logs_event_id_test_seq;

INSERT INTO events.logs_64_partitioned (event_id,udid_id,event_type_id,created,processed,deadline)
(select nextval('events_logs_event_id_test_seq'),1,1,t,'2000-01-01T00:00:00',t from(
SELECT generate_series('2000-01-01T00:00:00'::TIMESTAMP, '2000-12-31T00:00:00'::TIMESTAMP, '1 day') t) p);

INSERT INTO events.logs_64_partitioned (event_id,udid_id,event_type_id,created,processed,deadline)
VALUES (nextval('events_logs_event_id_test_seq'),1,1,'2000-12-31T00:00:00+0000','2000-12-31T23:01:00','2999-12-31T00:00:00+0000');

INSERT INTO events.logs_64_partitioned (event_id,udid_id,event_type_id,created,processed,deadline)
(select nextval('events_logs_event_id_test_seq'),2,1,t,'2000-01-01T00:00:00',t from(
SELECT generate_series('2000-01-01T00:00:00'::TIMESTAMP, '2000-02-01T00:00:00'::TIMESTAMP, '1 day') t) p);

DROP SEQUENCE events_logs_event_id_test_seq;

DELETE FROM events.logs_64_partitioned;
