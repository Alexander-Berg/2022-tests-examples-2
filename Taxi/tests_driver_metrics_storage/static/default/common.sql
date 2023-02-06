INSERT INTO common.udids (udid_id,udid,master_udid_id)VALUES
(1001,'100000000000000000000000',NULL),
(1002,'200000000000000000000000',NULL),
(1003,'300000000000000000000000',1001),
(1004,'400000000000000000000000',1001),
(1005,'500000000000000000000000',1001),
(1006,'600000000000000000000000',1001);

INSERT INTO common.event_types (event_type)VALUES
('type-X'),('type-Y'),('type-Z');

INSERT INTO common.tariff_zones (tariff_zone)VALUES
('moscow'),('spb');

INSERT INTO common.dbid_uuids (dbid_uuid) VALUES
('dbid_uuid1'),('dbid_uuid2'),
('park-id1_driver-profile-id1'),
('park-id2_driver-profile-id2');
