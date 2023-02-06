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
  'dbid_uuid3', -- wrong geobus heartbeated

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid4', -- not airport areas

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid5',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),

  'another_airport',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid6',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['business']::text[],
  ARRAY['business']::text[],

  '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
);
