INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  filtered_tp,
  offline_started_tp,
  queued,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  details
) VALUES
(
  'dbid_uuid1',

  'filtered',
  'blacklist',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '10 minute', -- updated
  NOW() - INTERVAL '10 minute', -- filtered_tp
  NULL, -- offline_started_tp
  NULL,

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid2',

  'filtered',
  'user_cancel',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '25 minute', -- updated
  NOW() - INTERVAL '25 minute', -- filtered_tp
  NULL, -- offline_started_tp
  NULL,

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid3',

  'entered',
  'old_mode',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW(), -- updated
  NOW(), -- filtered_tp
  NULL, -- offline_started_tp
  NULL,

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid4',

  'filtered',
  'driver_cancel',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '35 minute', -- updated
  NOW() - INTERVAL '35 minute', -- filtered_tp
  NULL, -- offline_started_tp
  NULL,

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid5',

  'filtered',
  'blacklist',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '8 minute', -- updated
  NOW() - INTERVAL '8 minute', -- filtered_tp
  NULL, -- offline_started_tp
  NULL,

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid6',

  'filtered',
  'user_cancel',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '2 minute', -- updated
  NOW() - INTERVAL '2 minute', -- filtered_tp
  NULL, -- offline_started_tp
  NULL,

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid7',

  'filtered',
  'offline',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '15 minute', -- updated
  NOW() - INTERVAL '15 minute', -- filtered_tp
  NOW(), -- offline_started_tp
  NULL,

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid8',

  'entered',
  'old_mode',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '4 minute', -- updated
  NOW() - INTERVAL '4 minute', -- filtered_tp
  NOW(), -- offline_started_tp
  NULL,

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_8", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid9',

  'filtered',
  'offline',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '2 minute', -- updated
  NOW() - INTERVAL '2 minute', -- filtered_tp
  NOW(), -- offline_started_tp
  NULL,

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_9", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid10',

  'filtered',
  'offline',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '15 minute', -- updated
  NOW() - INTERVAL '15 minute', -- filtered_tp
  NOW(), -- offline_started_tp
  NULL,

  'svo',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_10", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid11',

  'filtered',
  'offline',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '2 minute', -- updated
  NOW() - INTERVAL '2 minute', -- filtered_tp
  NOW(), -- offline_started_tp
  NULL,

  'svo',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_11", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid12',

  'filtered',
  'user_cancel',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '15 minute', -- updated
  NOW() - INTERVAL '15 minute', -- filtered_tp
  NULL, -- offline_started_tp
  NULL,

  'svo',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_12", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid13',

  'filtered',
  'offline',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '15 minute', -- updated
  NOW() - INTERVAL '15 minute', -- filtered_tp
  NOW(), -- offline_started_tp
  NULL,

  'spb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_13", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid14',

  'filtered',
  'blacklist',
  NOW(), -- entered
  NOW(), -- heartebeated
  NOW() - INTERVAL '10 minute', -- updated
  NULL, -- filtered_tp
  NULL, -- offline_started_tp
  NULL,

  'ekb',
  ARRAY[]::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_14", "lon": 1, "lat": 1}'::JSONB
);
