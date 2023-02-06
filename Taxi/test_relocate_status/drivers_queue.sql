INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  last_freeze_started_tp,
  queued,
  class_queued,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  details,
  car_number
) VALUES
(
  'dbid_uuid2',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'svo',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB,
  'car2'
),
(
  'dbid_uuid3',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB,
  'car3'
),
(
  'dbid_uuid4',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'svo',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB,
  'car4'
),
(
  'dbid_uuid5',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB,
  'car5'
),
(
  'dbid_uuid6',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'svo',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"unique_driver_id": "udid6", "session_id": "session_id6", "lon": 1, "lat": 1}'::JSONB,
  'car6'
),
(
  'dbid_uuid7',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"unique_driver_id": "udid7", "session_id": "session_id7", "lon": 1, "lat": 1}'::JSONB,
  'car7'
),
(
  'dbid_uuid8',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'svo',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"unique_driver_id": "udid8", "session_id": "session_id8", "lon": 1, "lat": 1}'::JSONB,
  'car8'
),
(
  'dbid_uuid9',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"unique_driver_id": "udid9", "session_id": "session_id9", "lon": 1, "lat": 1}'::JSONB,
  'car9'
),
(
  'dbid_uuid10',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"unique_driver_id": "udid10", "session_id": "session_id10", "lon": 1, "lat": 1}'::JSONB,
  'car10'
);
