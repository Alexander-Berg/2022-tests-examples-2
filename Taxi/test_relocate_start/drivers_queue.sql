INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  last_freeze_started_tp,
  queued,
  class_queued,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  details,
  car_number
) VALUES
(
  'dbid_uuid1',

  'queued',
  'on_tag',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NOW(),
  NULL,

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"unique_driver_id": "udid1", "session_id": "old_session_id1", "lon": 1, "lat": 1}'::JSONB,
  'a123bc'
),
(
  'dbid_uuid2',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'svo',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_2", "lon": 1, "lat": 1, "app_locale": "ru"}'::JSONB,
  'a123de'
),
(
  'dbid_uuid3',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NOW(),
  NULL,

  'svo',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_3", "lon": 1, "lat": 1, "app_locale": "ru"}'::JSONB,
  'a123fg'
),
(
  'dbid_uuid4',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NOW(),
  NULL,

  'svo',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"unique_driver_id": "udid4", "session_id": "session_id_4", "lon": 1, "lat": 1, "app_locale": "ru"}'::JSONB,
  'a123hi'
),
(
  'dbid_uuid5',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NOW(),
  NULL,

  'svo',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "old_session_id5", "lon": 1, "lat": 1, "app_locale": "ru"}'::JSONB,
  'a123jk'
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
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"unique_driver_id": "udid6", "session_id": "old_session_id6", "lon": 1, "lat": 1, "app_locale": "en"}'::JSONB,
  'a123lm'
),
(
    'dbid_uuid7',

    'queued',
    'on_tag',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NOW(),
    NULL,

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"unique_driver_id": "udid7", "session_id": "old_session_id7", "lon": 1, "lat": 1, "app_locale": "en"}'::JSONB,
    'a123no'
),
(
    'dbid_uuid8',

    'queued',
    'on_reposition_old_mode',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NOW(),
    NULL,

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"unique_driver_id": "udid8", "session_id": "old_session_id8", "lon": 1, "lat": 1, "app_locale": "en"}'::JSONB,
    'a123pq'
);
