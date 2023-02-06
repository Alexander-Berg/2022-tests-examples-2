-- noinspection SqlNoDataSourceInspectionForFile

INSERT INTO biometry_etalons.etalons
(
  id,
  version,
  modified,
  created,
  total_face_features_by_cbir,
  total_face_features_by_biometrics_features_v1
)
VALUES
(
  'e1',
  1,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000',
  0,
  1
),
(
  'e2',
  13,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000',
  NULL,
  NULL
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
  '{ "park_id": "p1" }',
  'unique_token',
  'e2'
),
(
  'y',
  'www_yyy',
  'park_driver_profile_id',
  'signalq',
  '{ "park_id": "p1" }',
  'unique_token_2',
  'e1'
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
  'xxx_yyy',
  'signalq-s3',
  'photo',
  'e2'
),
(
  '2',
  'x',
  'yyy',
  'yyy_yyy',
  'signalq-s3',
  'photo',
  'e2'
),
(
  '4',
  'x',
  'qqq',
  'qqq_yyy',
  'signalq-s3',
  'photo',
  'e2'
),
(
  '3',
  'y',
  'zzz',
  'zzz_yyy',
  'signalq-s3',
  'photo',
  'e1'
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
  '1',
  '1',
  '{1, 2, 4, 4}',
  '/biometrics_features/v1',
  'e2'
),
(
  '2',
  '2',
  '{3, 2, 4, 2}',
  '/biometrics_features/v1',  
  'e2'
),
(
  '5',
  '4',
  '{1, 2, 2, 4}',
  '/biometrics_features/v1',
  'e2'
),
(
  '3',
  '3',
  '{11, 2, 4, 0}',
  '/biometrics_features/v1',  
  'e1'
),
(
  '4',
  NULL,
  '{11, 2, 4, 0}',
  '/biometrics_features/v1',  
  'e1'
);
