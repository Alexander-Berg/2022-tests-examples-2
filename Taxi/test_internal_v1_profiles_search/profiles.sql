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
  '33d56564727d43a986318d1df5188df1',
  1,
  '2019-04-10 10:00:00.000000+03:00',
  '2019-04-10 10:00:00.000000+03:00'
),
(
  '55d56564727d43a986318d1df5188dg2',
  1,
  '2019-04-10 10:00:00.000000+03:00',
  '2019-04-10 10:00:00.000000+03:00'
);

INSERT INTO biometry_etalons.profiles
(
  id,
  profile_id,
  profile_type,
  provider,
  meta,
  idempotency_token,
  etalon_id,
  updated_at,
  created_at
)
VALUES 
(
  'x',
  'xxx_yyy',
  'park_driver_profile_id',
  'signalq',
  '{
      "park_id": "123",
      "device_serial": "d1",
      "park_id_car_id": "123_c1"
   }',
  'unique_token',
  '33d56564727d43a986318d1df5188df1',
  '2019-04-10 10:00:00.000000+03:00',
  '2018-04-10 10:00:00.000000+03:00'
),
(
  'y',
  'yyy_yyy',
  'park_driver_profile_id',
  'signalq',
  '{
      "park_id": "123",
      "device_serial": "d2",
      "park_id_car_id": "123_c2"
   }',
  'unique_token2',
  '55d56564727d43a986318d1df5188dg2',
  '2019-04-10 10:00:00.000000+03:00',
  '2019-03-10 10:00:00.000000+03:00'
),
(
  'z',
  'zzz_yyy',
  'park_driver_profile_id',
  'signalq',
  '{
      "park_id": "789",
      "device_serial": "d3",
      "park_id_car_id": "789_c3"
   }',
  'unique_token3',
  '55d56564727d43a986318d1df5188dg2',
  '2019-04-10 10:00:00.000000+03:00',
  '2019-04-12 10:00:00.000000+03:00'
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
  'y',
  'ms0000000000000000000001',
  'driver_photo',
  'media-storage',
  'photo',
  '55d56564727d43a986318d1df5188dg2'
);
