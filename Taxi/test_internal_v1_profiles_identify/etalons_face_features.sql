-- noinspection SqlNoDataSourceInspectionForFile

INSERT INTO biometry_etalons.etalons
(
  id,
  version,
  modified,
  created
)
VALUES
(
  '21d56564727d43a986318d1df5188df1',
  4,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  '33d56564727d43a986318d1df5188df1',
  13,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  '44d56564727d43a986318d1df5188df1',
  132,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
);

INSERT INTO biometry_etalons.profiles
(
  id,
  profile_id,
  profile_type,
  provider,
  meta,
  idempotency_token,
  etalon_id
)
VALUES 
(
  'x',
  'xxx_yyy',
  'park_driver_profile_id',
  'signalq',
  '{ "park_id": "123" }',
  'unique_token',
  '33d56564727d43a986318d1df5188df1'
),
(
  'k',
  'kkk_yyy',
  'park_driver_profile_id',
  'signalq',
  '{ "park_id": "123" }',
  'unique_token_2',
  '44d56564727d43a986318d1df5188df1'
),
(
  'z',
  'zzz_yyy',
  'park_driver_profile_id',
  'nesignalq',
  '{ "park_id": "1234" }',
  'unique_token_3',
  '44d56564727d43a986318d1df5188df1'
);

INSERT INTO biometry_etalons.media
(
  id,
  profile_id,
  media_storage_id,
  media_storage_bucket,
  media_storage_type,
  type,
  etalon_set_id
)
VALUES 
(
  '1',
  'x',
  'xxx',
  'yyy',
  'signalq-s3',
  'photo',
  '33d56564727d43a986318d1df5188df1'
),
(
  '2',
  'z',
  'zzz',
  'yyy',
  'signalq-s3',
  'photo',
  '44d56564727d43a986318d1df5188df1'
);


INSERT INTO biometry_etalons.face_features
(
  id,
  media_id,
  features,
  features_handler,
  etalon_id
)
VALUES 
(
  '2',
  '1',
  '{0.0625, 0.0625, 0.0635, 0.0624}',
  '/biometrics_features/v1',
  '33d56564727d43a986318d1df5188df1'
),
(
  '3',
  '2',
  '{-0.823, 0.023, 0.423, 0.923}',
  '/biometrics_features/v1',
  '44d56564727d43a986318d1df5188df1'
);
