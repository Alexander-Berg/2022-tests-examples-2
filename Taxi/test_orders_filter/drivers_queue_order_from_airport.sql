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
  'dbid_uuid1',

  'queued',
  'on_action',
  timestamptz '2020-05-01T21:00:00+00',                                -- entered
  timestamptz '2020-05-01T21:00:00+00',                                -- heartbeated
  timestamptz '2020-05-01T21:00:00+00',                                -- updated
  NULL,                                 -- input_order_finished_tp
  timestamptz '2020-05-01T21:00:00+00',                                -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'),  -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid2',

  'queued',
  'on_action',
  timestamptz '2020-05-01T21:00:00+00',                                -- entered
  timestamptz '2020-05-01T21:00:00+00',                                -- heartbeated
  timestamptz '2020-05-01T21:00:00+00',                                -- updated
  NULL,                                 -- input_order_finished_tp
  timestamptz '2020-05-01T21:00:00+00',                                -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'),  -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_2", "lon": 1, "lat": 1, "last_time_driver_had_order_from_airport": "2020-05-01T19:00:00+00"}'::JSONB
),
(
  'dbid_uuid3',

  'queued',
  'on_action',
  timestamptz '2020-05-01T21:00:00+00',                                -- entered
  timestamptz '2020-05-01T21:00:00+00',                                -- heartbeated
  timestamptz '2020-05-01T21:00:00+00',                                -- updated
  NULL,                                 -- input_order_finished_tp
  timestamptz '2020-05-01T21:00:00+00',                                -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'),  -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_3", "lon": 1, "lat": 1, "last_time_driver_had_order_from_airport": "2020-05-01T19:00:00+00"}'::JSONB
),
(
  'dbid_uuid4',

  'queued',
  'on_action',
  timestamptz '2020-05-01T21:00:00+00',                                -- entered
  timestamptz '2020-05-01T21:00:00+00',                                -- heartbeated
  timestamptz '2020-05-01T21:00:00+00',                                -- updated
  NULL,                                 -- input_order_finished_tp
  timestamptz '2020-05-01T21:00:00+00',                                -- queued
  jsonb_build_object('econom', timestamptz '2020-05-01T21:00:00+00', 'comfortplus', timestamptz '2020-05-01T21:00:00+00'),  -- class_queued

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
);
