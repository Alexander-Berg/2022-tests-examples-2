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
  'dbid_uuid3',

  'queued',
  'old_mode',
  NOW(),
  NOW() - INTERVAL '2 minute',
  NOW(),
  NOW(),
  jsonb_build_object('comfortplus', NOW(), 'business', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'business']::text[],
  ARRAY['comfortplus', 'business']::text[],

  '{
    "unique_driver_id": "3",
    "session_id": "session_id_3", "lon": 1, "lat": 1
  }'::JSONB
),
(
  'dbid_uuid4',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{
    "dms_queued_sent": true,
    "unique_driver_id": "4",
    "session_id": "session_id_4", "lon": 1, "lat": 1
  }'::JSONB
),
(
  'dbid_uuid5',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW() - INTERVAL '121 minute',
  jsonb_build_object('econom', NOW() - INTERVAL '121 minute', 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['comfortplus', 'econom']::text[],

  '{
    "unique_driver_id": "5",
    "session_id": "session_id_5", "lon": 1, "lat": 1
  }'::JSONB
),
(
  'dbid_uuid6',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{
    "unique_driver_id": "6",
    "session_id": "session_id_6", "lon": 1, "lat": 1
  }'::JSONB
);
