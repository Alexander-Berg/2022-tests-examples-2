INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  last_freeze_started_tp,
  left_queue_started_tp,
  no_classes_started_tp,
  forbidden_by_partner_started_tp,
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
  'dbid_uuid1',

  'entered',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid2',

  'filtered',
  'no_classes',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid3',

  'filtered',
  'full_queue',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid4',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '30 seconds', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '20 minutes',  -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '20 minutes', 'comfortplus', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '20 minutes'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid5',

  'filtered',
  'queued_gps',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '70 seconds', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid6',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  timestamptz '2020-05-01T21:00:00+00',  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '19 minutes', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '19 minutes', 'comfortplus', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '19 minutes'), -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid6_2',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  timestamptz '2020-05-01T21:00:00+00',  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2022-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2022-05-01T21:00:00+00', 'comfortplus', timestamptz '2022-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_6", "lon": 1, "lat": 1, "last_time_driver_had_order_from_airport": "2020-05-01T23:00:00+00"}'::JSONB
),
(
  'dbid_uuid7',

  'filtered',
  'filter_queued_left_zone',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid8',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '18 minutes', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '18 minutes'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_8", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid9',

  'filtered',
  'user_cancel',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_9", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid10',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '17 minutes', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '17 minutes', 'comfortplus', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '17 minutes'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_10", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid11',

  'filtered',
  'driver_cancel',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_11", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid12',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  timestamptz '2020-05-01T21:00:00+00', -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '110 minutes', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '110 minutes', 'comfortplus', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '110 minutes'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_12", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid13',

  'filtered',
  'max_queue_time',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '130 minutes', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '130 minutes', 'comfortplus', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '130 minutes'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_13", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid14',

  'filtered',
  'no_classes',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_14", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid15',

  'filtered',
  'holded',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_15", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid16',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '70 seconds',  -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  timestamptz '2020-05-01T21:00:00+00',  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '16 minutes', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '16 minutes', 'comfortplus', timestamptz '2020-05-01T21:00:00+00' - INTERVAL '16 minutes'), -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus', 'ultimate', 'business']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_16", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid17',

  'filtered',
  'wrong_client',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_17", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid18',

  'filtered',
  'not_airport_input_order',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_18", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid19',

  'filtered',
  'wrong_output_order',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'), -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_19", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid20',

  'filtered',
  'low_order_price',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_20", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid21',

  'filtered',
  'changed_tariff',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_21", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid22',

  'filtered',
  'offline',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_22", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid23',

  'filtered',
  'left_zone',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_23", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid24',

  'filtered',
  'gps',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_24", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid25',

  'entered',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '15 seconds',  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus', 'ultimate']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_25", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid26',

  'filtered',
  'freeze_expired',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  timestamptz '2020-05-01T21:00:00+00' - INTERVAL '35 minutes',  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  timestamptz '2020-05-01T21:00:00+00', -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'),  -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_26", "lon": 1, "lat": 1}'::JSONB
),
-- no classes warning
(
    'dbid_uuid27',

    'queued',
    'old_mode',
    timestamptz '2020-05-01T21:00:00+00', -- entered
    timestamptz '2020-05-01T21:00:00+00',  -- heartbeated
    timestamptz '2020-05-01T21:00:00+00', -- updated
    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    timestamptz '2020-05-01T21:00:00+00', -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp
    NULL,  -- offline_started_tp
    timestamptz '2020-05-01T21:00:00+00' - INTERVAL '16 minutes', -- queued
    NULL, -- class_queued

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_27", "lon": 1, "lat": 1}'::JSONB
),
-- all warnings: gps, no_classes and left_queue
(
    'dbid_uuid28',

    'queued',
    'old_mode',
    timestamptz '2020-05-01T21:00:00+00', -- entered
    timestamptz '2020-05-01T21:00:00+00' - INTERVAL '70 seconds',  -- heartbeated
    timestamptz '2020-05-01T21:00:00+00', -- updated
    NULL,  -- last_freeze_started_tp
    timestamptz '2020-05-01T21:00:00+00',  -- left_queue_started_tp
    timestamptz '2020-05-01T21:00:00+00' - INTERVAL '1800 seconds',  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp
    NULL,  -- offline_started_tp
    timestamptz '2020-05-01T21:00:00+00' - INTERVAL '16 minutes', -- queued
    NULL, -- class_queued

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_28", "lon": 1, "lat": 1}'::JSONB
),
-- all warnings: gps, left_queue and no_classes
(
    'dbid_uuid29',

    'queued',
    'old_mode',
    timestamptz '2020-05-01T21:00:00+00', -- entered
    timestamptz '2020-05-01T21:00:00+00' - INTERVAL '370 seconds',  -- heartbeated
    timestamptz '2020-05-01T21:00:00+00', -- updated
    NULL,  -- last_freeze_started_tp
    timestamptz '2020-05-01T21:00:00+00' - INTERVAL '15 seconds',  -- left_queue_started_tp
    timestamptz '2020-05-01T21:00:00+00',  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp
    NULL,  -- offline_started_tp
    timestamptz '2020-05-01T21:00:00+00' - INTERVAL '16 minutes', -- queued
    NULL, -- class_queued

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_29", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid30',

    'entered',
    'old_mode',
    timestamptz '2020-05-01T21:00:00+00', -- entered
    timestamptz '2020-05-01T21:00:00+00',  -- heartbeated
    timestamptz '2020-05-01T21:00:00+00', -- updated
    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NULL,  -- no_classes_started_tp
    timestamptz '2020-05-01T21:00:00+00' - INTERVAL '15 seconds',  -- forbidden_by_partner_started_tp
    NULL,  -- offline_started_tp
    NULL, -- queued
    NULL, -- class_queued

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_30", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid31',

    'entered',
    'no_classes',
    timestamptz '2020-05-01T21:00:00+00', -- entered
    timestamptz '2020-05-01T21:00:00+00', -- heartbeated
    timestamptz '2020-05-01T21:00:00+00', -- updated
    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    timestamptz '2020-05-01T21:00:00+00',  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp
    NULL,  -- offline_started_tp
    NULL,  -- queued
    NULL,  -- class_queued

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_31", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid32',

    'entered',
    'no_classes',
    timestamptz '2020-05-01T21:00:00+00', -- entered
    timestamptz '2020-05-01T21:00:00+00', -- heartbeated
    timestamptz '2020-05-01T21:00:00+00', -- updated
    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    timestamptz '2020-05-01T21:00:00+00',  -- no_classes_started_tp
    timestamptz '2020-05-01T21:00:00+00',  -- forbidden_by_partner_started_tp
    NULL,  -- offline_started_tp
    NULL,  -- queued
    NULL,  -- class_queued

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_32", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid33',

    'entered',
    'wrong_provider',
    timestamptz '2020-05-01T21:00:00+00', -- entered
    timestamptz '2020-05-01T21:00:00+00', -- heartbeated
    timestamptz '2020-05-01T21:00:00+00', -- updated
    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NULL,  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp
    NULL,  -- offline_started_tp
    NULL,  -- queued
    NULL,  -- class_queued

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_32", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid34',

    'entered',
    'old_mode',
    timestamptz '2020-05-01T21:00:00+00', -- entered
    timestamptz '2020-05-01T21:00:00+00',  -- heartbeated
    timestamptz '2020-05-01T21:00:00+00', -- updated
    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NULL,  -- no_classes_started_tp
    timestamptz '2020-05-01T21:00:00+00' - INTERVAL '75 seconds',  -- forbidden_by_partner_started_tp
    NULL,  -- offline_started_tp
    NULL, -- queued
    NULL, -- class_queued

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_34", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid35',

  'filtered',
  'offline',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_35", "lon": 1, "lat": 1, "taximeter_status": "off"}'::JSONB
),
(
  'dbid_uuid36',

  'filtered',
  'offline',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_36", "lon": 1, "lat": 1, "taximeter_status": "busy", "driver_very_busy_status": "verybusy"}'::JSONB
),
(
  'dbid_uuid37',

  'entered',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00', -- heartbeated
  timestamptz '2020-05-01T21:00:00+00', -- updated
  NULL,  -- last_freeze_started_tp
  NULL,  -- left_queue_started_tp
  NULL,  -- no_classes_started_tp
  NULL,  -- forbidden_by_partner_started_tp
  NULL,  -- offline_started_tp
  NULL,  -- queued
  NULL,  -- class_queued

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_37", "lon": 1, "lat": 1, "taximeter_status": "busy", "driver_very_busy_status": "verybusy"}'::JSONB
);

