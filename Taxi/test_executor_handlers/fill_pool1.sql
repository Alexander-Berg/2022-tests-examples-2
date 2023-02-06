INSERT INTO qc_pools.passes
	(id, entity_id, entity_type, exam, created)
VALUES ('id_dkvu_1', 'entity_id1', 'driver', 'dkvu', '2020-01-01T00:00:00+00:00'),
       ('id_dkvu_2', 'entity_id2', 'driver', 'dkvu', '2020-01-01T00:00:00+00:00'),
       ('id_dkvu_3', 'entity_id2', 'driver', 'dkvu', '2020-01-01T00:00:00+00:00'),
       ('id_dkk_1', 'entity_id1', 'driver', 'dkk', '2020-01-01T00:00:00+00:00'),
       ('id_dkk_2', 'entity_id2', 'driver', 'dkk', '2020-01-01T00:00:00+00:00');

INSERT INTO qc_pools.pools
(revision, pool, pass_id, status, created_at, expire_at)
VALUES (1,'pool1', 'id_dkvu_1', 'new','2020-01-01T00:00:00+00:00', '2020-01-02T00:00:00+00:00'),
       (2,'pool1', 'id_dkvu_2', 'new', '2020-01-01T00:00:00+00:00', '2020-01-02T00:00:00+00:00'),
       (3,'pool2', 'id_dkk_1', 'new', '2020-01-01T00:00:00+00:00', '2020-01-02T00:00:00+00:00'),
       (9223372036854775807,'pool3', 'id_dkvu_3', 'new', '2020-01-01T00:00:00+00:00', '2020-01-02T00:00:00+00:00');

INSERT INTO qc_pools.media
(pass_id, code, url, storage_id, storage_bucket)
VALUES ('id_dkvu_1', 'dkvu_front', 'http://dkvu_1_front.jpg', NULL, 'storage_bucket'),
       ('id_dkvu_1', 'dkvu_selfie', 'http://dkvu_1_selfie.jpg', NULL, NULL),
       ('id_dkvu_1', 'dkvu_back', 'http://dkvu_1_back.jpg', 'storage_id', 'storage_bucket'),
       ('id_dkvu_1', 'dkvu_side', 'http://dkvu_1_side.jpg', 'storage_id', NULL),
       ('id_dkvu_2', 'dkvu_front', 'http://dkvu_2_front.jpg', NULL, NULL),
       ('id_dkk_1', 'front', 'http://dkk_1_front.jpg', NULL, NULL),
       ('id_dkk_2', 'left', 'http://dkk_2_left.jpg', NULL, NULL);

INSERT INTO qc_pools.meta
(pass_id, key, value, data_type, json_value)
VALUES ('id_dkvu_1', 'quality-control.license_number', 'AAA111', 'string', '"AAA111"'),
       ('id_dkvu_1', 'quality-control.name', 'Иван', 'string', '"Иван"'),
       ('id_dkvu_1', 'quality-control.surname', 'Иванов', 'string', '"Иванов"'),
       ('id_dkvu_2', 'quality-control.license_number', 'AAA222', 'string', '"AAA222"'),
       ('id_dkvu_3', 'quality-control.license_pd_id', 'qc_license_pd_id', 'string', '"qc_license_pd_id"');
