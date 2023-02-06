INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  offline_started_tp,
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
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- offline_started_tp
  NOW(), -- queued
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_0", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid1',

  'queued',
  'old_mode',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- offline_started_tp
  NOW(), -- queued
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
);
