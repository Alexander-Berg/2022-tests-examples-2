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
  '2021-01-01T00:00:00+00:00',
  '2021-01-01T00:00:00+00:00',
  '2021-01-01T00:00:00+00:00',

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
);
