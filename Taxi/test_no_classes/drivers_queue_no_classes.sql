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
  'dbid_uuid0',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['comfortplus', 'econom']::text[],

  '{"session_id": "session_id_0", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid1',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['comfortplus', 'econom']::text[],

  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
);
