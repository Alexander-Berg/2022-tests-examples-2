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

  'order_id_1',
  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
);
