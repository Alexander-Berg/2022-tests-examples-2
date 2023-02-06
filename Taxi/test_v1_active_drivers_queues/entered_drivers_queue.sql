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

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('business', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['business']::text[],
  ARRAY['business']::text[],

  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid2',

  'filtered',
  'user_cancel',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid3',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('business', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['business']::text[],
  ARRAY['business']::text[],

  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
);
