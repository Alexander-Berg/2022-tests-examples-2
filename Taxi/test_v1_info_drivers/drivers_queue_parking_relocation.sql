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
  'dbid_uuid0',

  'queued',
  'old_mode',
  timestamptz '2020-05-01T21:00:00+00', -- entered
  timestamptz '2020-05-01T21:00:00+00' , -- heartbeated
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

  '{"session_id": "session_id_0", "lon": 1, "lat": 1, "parking_relocation_session": "repo0"}'::JSONB
),
(
  'dbid_uuid1',

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

  '{"session_id": "session_id_1", "lon": 1, "lat": 1, "parking_relocation_session": "repo1"}'::JSONB
),
(
  'dbid_uuid2',

  'entered',
  'on_reposition',
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
  ARRAY['econom', 'comfortplus', 'ultimate']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  '{"session_id": "session_id_2", "lon": 1, "lat": 1, "reposition_session_mode": "Sintegro", "reposition_target_airport_id": "svo"}'::JSONB
);

