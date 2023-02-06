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

  'svo',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "1", "lon": 1, "lat": 1}'::JSONB
);
