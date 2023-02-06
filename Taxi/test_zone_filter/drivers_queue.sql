INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  left_queue_started_tp,
  queued,
  class_queued,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  details
) VALUES
(
  'dbid_uuid1',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- left_queue_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid2',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL, -- left_queue_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid3',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '130 seconds', -- left_queue_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid3_1',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '130 seconds', -- left_queue_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_3_1", "lon": 1, "lat": 1, "last_time_driver_had_order_from_airport": "2020-05-01T20:00:00+00"}'::JSONB
),
(
  'dbid_uuid3_2',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '130 seconds', -- left_queue_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_3_2", "lon": 1, "lat": 1, "last_time_driver_had_order_from_airport": "2020-05-01T20:59:00+00"}'::JSONB
),
(
  'dbid_uuid4',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '110 seconds', -- left_queue_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid5',

  'entered',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- left_queue_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid6',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  timestamptz '2020-05-01T21:00:00+00', -- left_queue_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['main']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid8',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL, -- left_queue_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['waiting', 'main']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_8", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid9',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL, -- left_queue_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['waiting', 'main']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_9", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid10',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  timestamptz '2020-05-01T21:00:00+00', -- left_queue_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['main']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_10", "lon": 1, "lat": 1}'::JSONB
);
