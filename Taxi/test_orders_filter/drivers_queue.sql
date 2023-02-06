INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  input_order_finished_tp,
  queued,
  class_queued,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  input_order_id,
  details
) VALUES
(
  'dbid_uuid3',

  'entered',
  'on_action',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- input_order_finished_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'order_id_3',
  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid4',

  'entered',
  'on_action',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- input_order_finished_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'order_id_4',
  '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid5',

  'entered',
  'on_action',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- input_order_finished_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'order_id_5',
  '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid6',

  'queued',
  'on_action',
  NOW(),                                -- entered
  NOW(),                                -- heartbeated
  NOW(),                                -- updated
  NULL,                                 -- input_order_finished_tp
  NOW(),                                -- queued
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),  -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid7',

  'queued',
  'on_action',
  NOW(),                                -- entered
  NOW(),                                -- heartbeated
  NOW(),                                -- updated
  NULL,                                 -- input_order_finished_tp
  NOW(),                                -- queued
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),  -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid9',

  'entered',
  'on_action',
  NOW(),  -- entered
  NOW(),  -- heartbeated
  NOW(),  -- updated
  NULL,   -- input_order_finished_tp
  NULL,   -- queued
  NULL,   -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'order_id_9',
  '{"session_id": "session_id_9", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid10',

  'entered',
  'on_action',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- input_order_finished_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification', 'main']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'order_id_10',
  '{"session_id": "session_id_10", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid11',

  'entered',
  'on_action',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NOW(), -- input_order_finished_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'order_id_11',
  '{"unique_driver_id": "udid11", "session_id": "session_id_11", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid12',

  'entered',
  'on_action',
  NOW(),                          -- entered
  NOW(),                          -- heartbeated
  NOW(),                          -- updated
  NOW() - INTERVAL '61 minutes',  -- input_order_finished_tp
  NULL,                           -- queued
  NULL,                           -- class_queued

  'ekb',
  ARRAY['notification', 'main']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'order_id_12',
  '{"session_id": "session_id_12", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid13',

  'entered',
  'on_action',
  NOW(),                          -- entered
  NOW(),                          -- heartbeated
  NOW(),                          -- updated
  NOW() - INTERVAL '59 minutes',  -- input_order_finished_tp
  NULL,                           -- queued
  NULL,                           -- class_queued

  'ekb',
  ARRAY['notification', 'main']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'order_id_13',
  '{"session_id": "session_id_13", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid14',

  'entered',
  'old_mode',
  NOW(),      -- entered
  NOW(),      -- heartbeated
  NOW(),      -- updated
  NULL,       -- input_order_finished_tp
  NULL,       -- queued
  NULL,       -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_14", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid15',

  'entered',
  'old_mode',
  NOW(),    -- entered
  NOW(),    -- heartbeated
  NOW(),    -- updated
  NULL,     -- input_order_finished_tp
  NULL,     -- queued
  NULL,     -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'order_id_15',
  '{"session_id": "session_id_15", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid17',

  'queued',
  'on_action',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- input_order_finished_tp
  NOW(),                               -- queued
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'order_id_17',
  '{"session_id": "session_id_17", "lon": 1, "lat": 1}'::JSONB
);
