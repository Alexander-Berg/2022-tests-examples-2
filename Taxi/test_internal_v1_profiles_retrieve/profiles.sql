INSERT INTO biometry_etalons.etalons (id, VERSION, modified, created)
VALUES ('33d56564727d43a986318d1df5188df1', 1, '2019-04-10 10:00:00.000000', '2019-04-10 10:00:00.000000'),
       ('55d56564727d43a986318d1df5188dd5', 2, '2019-04-10 10:00:00.000000', '2019-04-10 10:00:00.000000'),
       ('11111164727d43a986318d1df1111111', 3, '2019-04-10 10:00:00.000000', '2019-04-10 10:00:00.000000'),
       ('nn22nn64727d43a986318d1d22nn22nn', 4, '2019-04-10 10:00:00.000000', '2019-04-10 10:00:00.000000');


INSERT INTO biometry_etalons.profiles (id, profile_id, profile_type, provider, meta, idempotency_token, etalon_id, updated_at)
VALUES ('x', 'xxx_yyy', 'park_driver_profile_id', 'signalq', '{ "park_id": "123" }', 'unique_token', '33d56564727d43a986318d1df5188df1', '2019-04-10 10:00:00.000000'),
       ('a', 'aaa_yyy', 'park_driver_profile_id', 'signalq', '{ "park_id": "123" }', 'unique_token4', '33d56564727d43a986318d1df5188df1', '2019-04-10 10:00:00.000000'),
       ('y', 'yyy_yyy', 'park_driver_profile_id', 'signalq', '{ "park_id": "123" }', 'unique_token2', '55d56564727d43a986318d1df5188dd5', '2019-04-10 10:00:00.000000'),
       ('z', 'zzz_yyy', 'park_driver_profile_id', 'signalq', '{ "park_id": "789" }', 'unique_token3', '55d56564727d43a986318d1df5188dd5', '2019-04-10 10:00:00.000000'),
       ('w', 'www_ttt', 'park_driver_profile_id', 'signalq', '{ "park_id": "789" }', 'unique_token5', '11111164727d43a986318d1df1111111', '2019-04-10 10:00:00.000000'),
       ('n', 'nnn_mmm', 'park_driver_profile_id', 'signalq', '{ "park_id": "789" }', 'unique_token6', 'nn22nn64727d43a986318d1d22nn22nn', '2019-04-10 10:00:00.000000');


INSERT INTO biometry_etalons.media (id, profile_id, media_storage_id, media_storage_bucket, media_storage_type, TYPE, etalon_set_id, is_active)
VALUES ('1', 'x', 'xxx', 'yyy', 'signalq-s3', 'photo', '33d56564727d43a986318d1df5188df1', TRUE),
       ('2', 'y', 'ms0000000000000000000001', 'driver_photo', 'media-storage', 'photo', '55d56564727d43a986318d1df5188dd5', TRUE),
       ('3', 'a', 'xxx2', 'yyy2', 'signalq-s3', 'photo', '33d56564727d43a986318d1df5188df1', TRUE),
       ('4', 'y', 'ms0000000000000000000001', 'driver_photo', 'media-storage', 'photo', '55d56564727d43a986318d1df5188dd5', FALSE),
       ('5', 'w', 'ms0000000000000000000001', 'driver_photo', 'media-storage', 'photo', '11111164727d43a986318d1df1111111', TRUE);


INSERT INTO biometry_etalons.face_features (id, features, etalon_id, media_id, features_handler, deleted)
VALUES ('face_features_id_1', ARRAY[1.1,1.1,1.1], '33d56564727d43a986318d1df5188df1', '1', 'signalq', FALSE),
       ('face_features_id_2', ARRAY[2.2,2.2,2.2], '55d56564727d43a986318d1df5188dd5', '2', '/biometrics_features/v1', FALSE),
       ('face_features_id_3', ARRAY[3.3,3.3,3.3], '33d56564727d43a986318d1df5188df1', '3', 'signalq', FALSE),
       ('face_features_id_4', ARRAY[4.4,4.4,4.4], '33d56564727d43a986318d1df5188df1', '3', '/biometrics_features/v1', FALSE),
       ('face_features_id_5', ARRAY[5.5,5.5,5.5], '55d56564727d43a986318d1df5188dd5', '2', 'signalq', TRUE);


INSERT INTO biometry_etalons.media_meta (id, media_id, KEY, value)
VALUES ('meta_id_1', '1', 'meta_key_1', 'meta_value_1'),
       ('meta_id_2', '1', 'meta_key_2', 'meta_value_2'),
       ('meta_id_3', '3', 'meta_key_3', 'meta_value_3'),
       ('meta_id_4', '4', 'meta_key_4', 'meta_value_4'),
       ('meta_id_5', '5', 'meta_key_5', 'meta_value_5');
