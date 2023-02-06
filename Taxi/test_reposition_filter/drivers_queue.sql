INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  filtered_tp,
  queued,
  class_queued,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  reposition_session_id,
  details
) VALUES
(
  'dbid_uuid3',

  'entered',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'session_dbid_uuid3',
  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid6',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NOW(),
  jsonb_build_object('comfortplus', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid7',

  'entered',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'ekb',
  ARRAY['main']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'session_dbid_uuid7',
  '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid11',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_11", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid12',

  'entered',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'ekb',
  ARRAY['waiting', 'main']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'session_dbid_uuid12',
  '{"session_id": "session_id_12", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid13',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_13", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid15',

    'entered',
    'on_reposition_old_mode',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,
    NULL,

    'ekb',
    ARRAY['main', 'notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'rsid_15',
    '{"session_id": "session_id_15", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid16',

    'filtered',
    'user_cancel',
    NOW(),
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['main']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    NULL,
    '{"session_id": "session_id_16", "lon": 1, "lat": 1}'::JSONB
);
