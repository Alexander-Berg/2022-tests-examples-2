insert into common.udids (udid_id,udid,master_udid_id)values
(1001,'100000000000000000000000',null),
(1002,'200000000000000000000000',null),
(1003,'300000000000000000000000',1001),
(1004,'400000000000000000000000',1001),
(1005,'500000000000000000000000',1001),
(1006,'600000000000000000000000',1001);
insert into common.event_types (event_type_id,event_type)values(1,'type-x');

create sequence events_logs_event_id_test_seq;
insert into events.queue_64 (event_id,udid_id,event_type_id,created,deadline)
(select nextval('events_logs_event_id_test_seq'),1001,1,t,'2999-01-01t00:00:00+0000' from(
select generate_series('2000-01-01t00:00:00'::timestamp, '2000-12-31t00:00:00'::timestamp, '1 day') t) p);
drop sequence events_logs_event_id_test_seq;

insert into data.logs_64_partitioned (event_id,udid_id,created,loyalty_increment,activity_increment)
(select event_id,udid_id,created,0,0 from events.logs_64_partitioned);

INSERT INTO data.activity_values (udid_id,value,complete_score_value,updated)VALUES
(1001,99,140,'2019-01-01T00:00:00'),
(1002,99,10,'2019-01-01T00:00:00'),
(1003,99,-3,'2019-01-01T00:00:00');

INSERT INTO data.activity_values_generations (udid_id,generation)
VALUES (1001,NULL),(1002,NULL),(1003,NULL);
