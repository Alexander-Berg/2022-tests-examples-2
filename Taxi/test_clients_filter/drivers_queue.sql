INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  queued,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  details
) VALUES
(
  'dbid_uuid6',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_6", "valid_client": true, "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid7',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['comfortplus', 'econom']::text[],

  '{"session_id": "session_id_7", "valid_client": true, "lon": 1, "lat": 1}'::JSONB
);
