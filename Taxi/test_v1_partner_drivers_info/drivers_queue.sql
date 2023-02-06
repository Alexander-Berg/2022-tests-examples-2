INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  queued,
  class_queued,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  details
) VALUES
(
  'dbid_uuid1',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid2',

  'filtered',
  'no_classes',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid3',

  'filtered',
  'full_queue',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid4',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  '2021-08-19T10:03:45+0000',
  jsonb_build_object('econom', '2021-08-19T10:03:46+0000', 'comfortplus', '2021-08-19T10:03:47+0000'),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid5',

  'filtered',
  'holded',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid6',

  'filtered',
  'driver_cancel',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid7',

  'queued',
  'on_action',
  NOW(),
  NOW(),
  NOW(),
  '2021-08-19T10:03:48+0000',
  jsonb_build_object('econom', '2021-08-19T10:03:49+0000', 'comfortplus', '2021-08-19T10:03:50+0000'),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
);
