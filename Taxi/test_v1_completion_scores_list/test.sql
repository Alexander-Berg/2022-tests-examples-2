INSERT INTO events.logs_64_partitioned (event_id,udid_id,event_type_id,created,deadline,processed) VALUES
(1,1002,1,'2000-01-01T00:00:00','2050-01-01T00:00:00','2000-01-01T00:01:00'),
(2,1004,2,'2000-01-01T01:00:00','2050-01-01T01:00:00','2000-01-01T01:01:00');

INSERT INTO data.activity_values (udid_id,value,complete_score_value,updated) VALUES
(1002,222,201,'2000-01-01T00:00:00'),
(1004,444,401,'2000-01-01T00:00:00');

INSERT INTO data.activity_values_generations (udid_id,generation)VALUES
(1002,nextval('data.activity_values_generation_sequence')),
(1004,NULL);

INSERT INTO events.queue_64 (event_id,udid_id,event_type_id,created,deadline,activation) VALUES
(3,1002,1,'2000-01-01T00:00:00','2000-01-01T00:00:00','2000-01-01T00:00:00'),
(4,1004,1,'2000-01-01T00:00:00','2000-01-01T00:00:00','2000-01-01T00:00:00');
