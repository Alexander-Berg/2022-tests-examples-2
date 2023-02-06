INSERT INTO common.udids (udid_id,udid,master_udid_id)VALUES
(1001,'000000000000000000000001',NULL);
       

INSERT INTO common.event_types (event_type_id, event_type) VALUES
	(1, 'type-X'),
	(2, 'type-Y'),
	(3, 'type-Z'),
	(4, 'order'),
	(5, 'dm_service_manual');
INSERT INTO common.tariff_zones (tariff_zone_id, tariff_zone) VALUES (1, 'moscow'),(2, 'spb');
INSERT INTO common.dbid_uuids (dbid_uuid_id, dbid_uuid) VALUES (1, '000000000000000000000101_000000000000000000000101'),(2, '000000000000000000000202_000000000000000000000202');
						  

INSERT INTO data.activity_values (udid_id,value,updated)VALUES
(1001,50,'2019-01-01T00:00:00');

INSERT INTO data.activity_values_generations (udid_id,generation)VALUES
(1001,nextval('data.activity_values_generation_sequence'));

INSERT INTO data.logs_64_partitioned_1_mod_20 (event_id,udid_id,created,loyalty_increment,activity_increment) VALUES
(1,1001,'2019-01-01T00:00:01+0000',15,6),
(2,1001,'2019-01-01T00:00:02+0000',16,7),
(3,1001,'2019-01-01T00:00:02+0000',null,-8);


INSERT INTO events.logs_64_partitioned (
	event_id, udid_id, event_type_id, tariff_zone_id,
	created, deadline, order_id, order_alias,
	processed, dbid_uuid_id,
	descriptor, extra_data) VALUES
(1,1001,4,1,
	'2019-01-01T00:00:01+0000','2099-01-02T00:00:00+0000','order_id_1',NULL,
	'2019-01-01T00:00:01+0000',1,
	'{"type":"user_test","tags":["yam-yam","tas_teful"]}',
	'{"extra_field":"0"}'),
(2,1001,4,1,
	'2019-01-01T00:00:02+0000','2099-01-02T00:00:00+0000','order_id_2',NULL,
	'2019-01-01T00:00:02+0000',1,
	'{"type":"user_test","tags":["yam-yam","tas_teful"]}',
	concat(
		'{"extra_field":"1",',
		'"db_id":"000000000000000000030303",',
		'"driver_id":"32gdh3_dad8lucn58003nnbc3",',
		'"distance_to_a":5.0,',
		'"time_to_a":120.0,',
		'"dispatch_traits":{"distance":"long"}}')),
(3,1001,5, null,
	'2019-01-01T00:00:00+0000', '2099-01-02T00:00:00+0000', null, null,
	'2019-01-01T00:00:00+0000', null,
	'{"type":"set_activity_value"}',
	concat(
		'{"operation":"set_activity_value",',
		'"mode":"absolute",'
		'"value":100,',
		'"reason":"a70ef681db7b2ff2b4ee23daeebf4ca3"}'));
