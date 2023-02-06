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
  'dbid_uuid1',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid2',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid3',

  'filtered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
);
