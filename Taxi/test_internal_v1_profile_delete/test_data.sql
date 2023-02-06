INSERT INTO biometry_etalons.etalons
(
  id,
  version,
  modified,
  created
)
VALUES
(
  'e1',
  1,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  'e2',
  1,
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
  'p1_d1',
  'park_driver_profile_id',
  'signalq',
  '{ "park_id": "p1" }',
  'unique_token',
  'e1'
),
(
  'z',
  'p1_d3',
  'park_driver_profile_id',
  'signalq',
  '{ "park_id": "p1" }',
  'unique_token_1',
  'e1'
),
(
  'y',
  'p1_d2',
  'park_driver_profile_id',
  'signalq',
  '{ "park_id": "p1" }',
  'unique_token_2',
  'e2'
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
  'y',
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
  'zyy',
  'zyy_yyy',
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
  '3',
  '3',
  '{3, 2, 4, 2}',
  '/biometrics_features/v1',  
  'e1'
);
