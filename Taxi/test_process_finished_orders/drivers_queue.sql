INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  queued,
  class_queued,

  airport,
  areas,
  classes,
  taximeter_tariffs,

  car_id,
  input_order_id,

  details
) VALUES
(
  'dbid_uuid1',

  'entered',
  'on_action',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus', 'vip']::text[],
  ARRAY['econom', 'comfortplus', 'vip']::text[],

  'car_id1',
  'some_input_order1',
  '{"session_id": "session_id_1", "lon": 1, "lat": 1, "unique_driver_id": "udid1"}'::JSONB
),
(
  'dbid_uuid2',

  'entered',
  'on_action',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('vip', NOW()),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['vip']::text[],
  ARRAY['vip']::text[],

  'car_id2',
  'some_input_order2',
  '{"session_id": "session_id_2", "lon": 1, "lat": 1, "unique_driver_id": "udid2"}'::JSONB
),
(
  'dbid_uuid3',

  'entered',
  'on_action',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('business', NOW()),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['business']::text[],
  ARRAY['business']::text[],

  'car_id3',
  'some_input_order3',
  '{"session_id": "session_id_3", "lon": 1, "lat": 1, "unique_driver_id": "udid3"}'::JSONB
),
(
  'dbid_uuid4',

  'entered',
  'on_action',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus', 'vip']::text[],
  ARRAY['econom', 'comfortplus', 'vip']::text[],

  'car_id4',
  'some_input_order4',
  '{"session_id": "session_id_4", "lon": 1, "lat": 1, "unique_driver_id": "udid4"}'::JSONB
),
(
  'dbid_uuid5',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus', 'vip']::text[],
  ARRAY['econom', 'comfortplus', 'vip']::text[],

  'car_id5',
  NULL,
  '{"session_id": "session_id_5", "lon": 1, "lat": 1, "unique_driver_id": "udid5"}'::JSONB
)
;
