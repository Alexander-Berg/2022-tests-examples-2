INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  details
) VALUES
(
  'dbid_uuid8',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_8", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid9',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),

  'svo',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_9", "lon": 1, "lat": 1}'::JSONB
);
