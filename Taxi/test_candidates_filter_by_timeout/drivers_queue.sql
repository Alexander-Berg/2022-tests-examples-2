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
  'dbid_uuid10',

  'queued',
  'on_reposition',
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
    "session_id": "session_id_10",
    "unique_driver_id": "10",
    "lon": 1, "lat": 1
  }'::JSONB
),
(
    'dbid_uuid11',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NOW(),
    jsonb_build_object('econom', NOW()),

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    '{
      "session_id": "session_id_11",
      "unique_driver_id": "11",
      "lon": 1, "lat": 1
    }'::JSONB
);
