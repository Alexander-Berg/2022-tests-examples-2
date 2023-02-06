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

  input_order_id,
  reposition_session_id,
  details
) VALUES
(
  'dbid_uuid10',

  'queued',
  'on_action',

  NOW(),
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'input_order_10',
  NULL,
  '{"unique_driver_id": "udid10", "session_id": "session_id10", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid11',

  'entered',
  'on_repeat_queue',

  NOW(),
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  NULL,
  '{"unique_driver_id": "udid11", "session_id": "session_id11", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid12',

  'entered',
  'on_repeat_queue',

  NOW(),
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY['waiting', 'notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  NULL,
  '{"unique_driver_id": "udid12", "session_id": "session_id12", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid13',

  'entered',
  'on_repeat_queue',

  NOW(),
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY['waiting', 'notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  NULL,
  '{"unique_driver_id": "udid13", "session_id": "session_id13", "lon": 1, "lat": 1}'::JSONB
);
