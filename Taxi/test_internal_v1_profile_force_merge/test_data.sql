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
  NULL,
  NULL
),
(
  'e2',
  13,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000',
  0,
  2
),
(
  'e3',
  55,
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
  'e2'
),
(
  'z',
  'sss_yyy',
  'park_driver_profile_id',
  'signalq',
  '{ "park_id": "p1" }',
  'unique_token_3',
  'e1'
),
(
  'a',
  'aaa_yyy',
  'anonymous',
  'signalq',
  '{ "park_id": "p1" }',
  'unique_token_4',
  'e3'
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
  'y',
  'yyy',
  'yyy_yyy',
  'signalq-s3',
  'photo',
  'e2'
),
(
  '3',
  'z',
  'zzz1',
  'zzz_yyy1',
  'signalq-s3',
  'photo',
  'e1'
),
(
  '4',
  'z',
  'zzz2',
  'zzz_yyy2',
  'signalq-s3',
  'photo',
  'e1'
),
(
  '5',
  'z',
  'zzz3',
  'zzz_yyy3',
  'signalq-s3',
  'photo',
  'e1'
),
(
  '6',
  'a',
  'aaa3',
  'aaa_yyy3',
  'signalq-s3',
  'photo',
  'e3'
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
  '4',
  NULL,
  '{2, 2, 4, 3}',
  '/biometrics_features/v1',
  'e2'
),
(
  '3',
  '3',
  '{2, 2, 3, 4}',
  '/biometrics_features/v1',
  'e1'
),
(
  '5',
  '4',
  '{2, 3, 4, 1}',
  '/biometrics_features/v1',
  'e1'
),
(
  '6',
  '5',
  '{2, 1, 2, 1}',
  '/biometrics_features/v1',
  'e1'
),
(
  '7',
  '6',
  '{2, 3, 4, 1}',
  'cbir',
  'e3'
);
