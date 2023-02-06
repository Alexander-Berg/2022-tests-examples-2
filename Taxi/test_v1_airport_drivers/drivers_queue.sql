INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  offline_started_tp,
  queued,
  class_queued,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  car_number,
  car_id,
  details
) VALUES
(
  'dbid_uuid1',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  '2021-01-01T00:00:00+00:00',
  NULL, -- offline_started_tp
  NOW(),
  jsonb_build_object('econom', '2021-01-01T00:00:00+00:00'),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  'У555УУ178',
  'car_id1',

  '{"session_id": "session_id_1", "lat": 1, "lon": 2}'::JSONB
),
(
  'dbid_uuid2',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  '2021-01-01T02:00:00+00:00',
  NULL, -- offline_started_tp
  NOW(),
  jsonb_build_object('econom', '2021-01-01T01:00:00+00:00',
                     'comfortplus', '2021-01-01T02:00:00+00:00'),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'У556УУ178',
  'car_id2',

  '{"session_id": "session_id_2", "lat": 1, "lon": 2}'::JSONB
),
(
  'dbid_uuid3',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  '2021-01-01T00:00:00+00:00',
  NOW(), -- offline_started_tp
  NULL,
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  NULL,
  '{"session_id": "session_id_3", "lat": 3, "lon": 4}'::JSONB
),
(
  'dbid_uuid4',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  '2021-01-01T00:00:00+00:00',
  NULL, -- offline_started_tp
  NOW(),
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  NULL,
  '{"session_id": "session_id_4", "lat": 5, "lon": 6}'::JSONB
),
(
  'dbid_uuid6',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  '2021-01-01T00:00:00+00:00',
  NULL, -- offline_started_tp
  NULL,
  NULL,

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  NULL,
  '{"session_id": "session_id_6", "lat": 3, "lon": 4}'::JSONB
),
(
  'dbid_uuid7',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  '2021-01-01T00:00:00+00:00',
  NULL, -- offline_started_tp
  NOW(),
  NULL,

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  NULL,
  '{"session_id": "session_id_7", "lat": 3, "lon": 4}'::JSONB
),
(
  'dbid_uuid8',

  'filtered',
  'offline',
  NOW(),
  NOW(),
  NOW(),
  NOW(), -- offline_started_tp
  NOW(),
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  NULL,
  '{"session_id": "session_id_8", "lat": 3, "lon": 4}'::JSONB
),
(
  'dbid_uuid9',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  '2021-01-01T00:00:00+00:00',
  NULL, -- offline_started_tp
  NULL,
  NULL,

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  NULL,
  '{"session_id": "session_id_9", "lat": 3, "lon": 4}'::JSONB
),
(
  'dbid_uuid10',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  '2021-01-01T00:00:00+00:00',
  NULL, -- offline_started_tp
  NOW(),
  jsonb_build_object('econom', '2021-01-01T03:00:00+00:00', 'comfortplus', '2021-01-01T04:00:00+00:00'),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  NULL,
  '{"session_id": "session_id_10", "lat": 3, "lon": 4}'::JSONB
);
