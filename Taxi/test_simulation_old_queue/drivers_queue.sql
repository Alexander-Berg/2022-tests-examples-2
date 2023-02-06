INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  offline_started_tp,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  reposition_session_id,
  details
) VALUES
(
  'dbid_uuid4',

  'entered',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'session_dbid_uuid4',
  '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid5',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid6',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,

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
  '',
  NOW(),
  NOW(),
  NOW(),
  NULL,

  'ekb',
  ARRAY['main']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid10',

    'entered',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NOW(),

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    NULL,
    '{"session_id": "session_id_10", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid11',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NOW(),

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'rid11',
    '{"session_id": "session_id_11", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid12',

    'entered',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NOW(),

    'ekb',
    ARRAY['notification', 'main', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    NULL,
    '{"session_id": "session_id_12", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid13',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NOW(),

    'ekb',
    ARRAY['notification', 'main', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'rid12',
    '{"session_id": "session_id_13", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid14',

    'entered',
    'offline',
    NOW(),
    NOW(),
    NOW(),
    NULL,

    'ekb',
    ARRAY['notification', 'main', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    NULL,
    '{"session_id": "session_id_15", "lon": 1, "lat": 1}'::JSONB
);
