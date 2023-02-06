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
  'dbid0_uuid0',

  'queued',
  'on_action',
  NOW(),
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['comfortplus', 'econom']::text[],

  'input_order_0',
  NULL,
  '{"unique_driver_id": "udid0", "session_id": "old_session_id0", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid1_uuid1',

  'queued',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['comfortplus', 'econom']::text[],

  NULL,
  'reposition_session_1',
  '{"unique_driver_id": "udid1", "session_id": "old_session_id1", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid3_uuid3',

  'queued',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['comfortplus', 'econom']::text[],

  NULL,
  'reposition_session_3',
  '{"unique_driver_id": "udid3", "session_id": "old_session_id3", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid4_uuid4',

  'queued',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['comfortplus', 'econom']::text[],

  NULL,
  'reposition_session_4',
  '{"unique_driver_id": "udid4", "session_id": "old_session_id4", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid5_uuid5',

  'queued',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NOW() - INTERVAL '31 minutes',

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['comfortplus', 'econom']::text[],

  NULL,
  'reposition_session_5',
  '{"unique_driver_id": "udid5", "session_id": "old_session_id5", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid6_uuid6',

  'queued',
  'on_action',
  NOW(),
  NOW(),
  NOW(),
  NOW(),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['comfortplus', 'econom']::text[],

  'input_order_6',
  NULL,
  '{"unique_driver_id": "udid6", "session_id": "new_session_id6", "lon": 1, "lat": 1}'::JSONB
);
