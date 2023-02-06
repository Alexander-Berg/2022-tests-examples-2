INSERT INTO qc_pools.passes
	(id, entity_id, entity_type, exam, created)
VALUES ('id_dkvu_1', 'entity_id1', 'driver', 'dkvu', '2020-01-01T00:00:10+00:00'),
       ('id_dkvu_2', 'entity_id2', 'driver', 'dkvu', '2020-01-01T00:00:01+00:00'),
       ('id_dkvu_3', 'entity_id3', 'driver', 'dkvu', '2020-01-01T00:00:00+00:00'),
       ('id_dkvu_4', 'entity_id4', 'driver', 'dkvu', '2020-01-01T00:00:20+00:00'),
       ('id_dkvu_5', 'entity_id5', 'driver', 'dkvu', '2020-01-01T00:00:02+00:00'),
       ('id_dkvu_6', 'entity_id6', 'driver', 'dkvu', '2020-01-01T00:00:30+00:00'),
       ('id_dkvu_33', 'entity_id33', 'driver', 'dkvu', '2020-01-01T00:00:30+00:00'),
       ('id_dkvu_34', 'entity_id34', 'driver', 'dkvu', '2020-01-01T00:00:30+00:00'),
       ('id_dkvu_35', 'entity_id35', 'driver', 'dkvu', '2020-01-01T00:00:30+00:00');


INSERT INTO qc_pools.pools
(revision, pool, pass_id, status, created_at, expire_at)
VALUES (1,'pool1', 'id_dkvu_1', 'new','2020-01-01T00:00:01+00:00', '2020-01-02T00:00:00+00:00'),
       (2,'pool1', 'id_dkvu_2', 'new', '2020-01-01T00:00:02+00:00', '2020-01-02T00:00:00+00:00'),
       (4,'pool1', 'id_dkvu_4', 'new', '2020-01-01T00:00:04+00:00', '2020-01-02T00:00:00+00:00'),
       (5,'pool1', 'id_dkvu_5', 'new','2020-01-01T00:00:05+00:00', '2020-01-02T00:00:00+00:00'),
       (3,'pool1', 'id_dkvu_3', 'new','2020-01-01T00:00:05+00:00', '2020-01-02T00:00:00+00:00'),
       (6,'pool1', 'id_dkvu_6', 'new', '2020-01-01T00:00:06+00:00', '2020-01-02T00:00:00+00:00'),
       (33,'pool1', 'id_dkvu_33', 'new','2020-01-01T00:00:33+00:00', '2020-01-02T00:00:00+00:00'),
       (34,'pool2', 'id_dkvu_34', 'new','2020-01-01T00:00:33+00:00', '2020-01-02T00:00:00+00:00'),
       (35,'pool3', 'id_dkvu_35', 'new','2020-01-01T00:00:33+00:00', '2020-01-02T00:00:00+00:00');



INSERT INTO qc_pools.media
(pass_id, code, url)
VALUES ('id_dkvu_1', 'dkvu_front', 'http://dkvu_1_front.jpg'),
       ('id_dkvu_1', 'dkvu_selfie', 'http://dkvu_1_selfie.jpg'),
       ('id_dkvu_2', 'dkvu_front', 'http://dkvu_2_front.jpg');

INSERT INTO qc_pools.meta
(pass_id, key, value, data_type, json_value)
VALUES ('id_dkvu_1', 'quality-control.license_number', 'AAA111', 'string', '"AAA111"'),
       ('id_dkvu_1', 'quality-control.name', 'Иван', 'string', '"Иван"'),
       ('id_dkvu_1', 'quality-control.surname', 'Иванов', 'string', '"Иванов"'),
       ('id_dkvu_2', 'quality-control.license_number', 'AAA222', 'string', '"AAA222"'),
       ('id_dkvu_34', 'string', 'AAA111', 'string', '"AAA111"'),
       ('id_dkvu_34', 'set_string', '["AAA222"]', 'set_string', '["AAA222"]'),
       ('id_dkvu_34', 'bool', 'true', 'bool', 'true'),
       ('id_dkvu_34', 'int', 'AAA222', 'int', '11'),
       ('id_dkvu_35', 'license_pd_id', 'license_pd_id3', 'string', '"license_pd_id3"');
