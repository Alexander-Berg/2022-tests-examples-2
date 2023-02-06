INSERT INTO eta_autoreorder.orders
(
  id,
  last_event_handled,
  updated,
  zone_id,
  tariff_class,
  performer_dbid_uuid,
  performer_assigned,
  performer_initial_eta,
  performer_initial_distance,
  first_performer_assigned,
  first_performer_initial_eta,
  first_performer_initial_distance,
  eta_autoreorders_count,
  last_event,
  user_phone_id,
  performer_cp_id,
  point_a,
  destinations,
  requirements
)
VALUES
-- new order which has enabled rule:
(
  'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', -- id
  '2020-01-01T12:01:00', -- last_event_handled
  '2020-01-01T12:01:00', -- updated
  'moscow', -- zone_id,
  'vip', --tariff_class
  '00000000000000000000000000000000_11111111111111111111111111111111', -- performer_dbid_uuid
  '2020-01-01T12:00:00', -- performer_assigned
  INTERVAL '300 seconds', -- performer_initial_eta
  5000, -- performer_initial_distance
  '2020-01-01T12:00:00', -- first_performer_assigned
  INTERVAL '300 seconds', -- first_performer_initial_eta
  5000, -- first_performer_initial_distance
  0, -- eta_autoreorders_count
  'handle_driving', -- last_event
  '111111111111111111111111', -- user_phone_id
  'cccccccccccccccccccccccccccccccc', -- performer_cp_id
  '{20.123123, 30.123123}', -- point_a
  '{}', -- destinations
  '{}' -- requirements
),
-- new order which doesn't have enabled rule:
(
  'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', -- id
  '2020-01-01T12:01:00', -- last_event_handled
  '2020-01-01T12:01:00', -- updated
  'moscow', -- zone_id,
  'vip', --tariff_class
  '00000000000000000000000000000000_11111111111111111111111111111111', -- performer_dbid_uuid
  '2020-01-01T12:00:00', -- performer_assigned
  INTERVAL '300 seconds', -- performer_initial_eta
  5000, -- performer_initial_distance
  '2020-01-01T12:00:00', -- first_performer_assigned
  INTERVAL '300 seconds', -- first_performer_initial_eta
  5000, -- first_performer_initial_distance
  0, -- eta_autoreorders_count
  'handle_driving', -- last_event
  '111111111111111111111111', -- user_phone_id
  Null, -- performer_cp_id
  '{20.123123, 30.123123}', -- point_a
  '{}', -- destinations
  '{}' -- requirements
),
-- parent order for first order
(  
  'cccccccccccccccccccccccccccccccc', -- id
  '2020-01-01T12:01:00', -- last_event_handled
  '2020-01-01T12:01:00', -- updated
  'moscow', -- zone_id,
  'vip', --tariff_class
  '00000000000000000000000000000000_11111111111111111111111111111111', -- performer_dbid_uuid
  '2020-01-01T12:00:00', -- performer_assigned
  INTERVAL '300 seconds', -- performer_initial_eta
  5000, -- performer_initial_distance
  '2020-01-01T12:00:00', -- first_performer_assigned
  INTERVAL '300 seconds', -- first_performer_initial_eta
  5000, -- first_performer_initial_distance
  0, -- eta_autoreorders_count
  'handle_driving', -- last_event
  '111111111111111111111111', -- user_phone_id
  Null, -- performer_cp_id
  '{20.123123, 30.123123}', -- point_a
  '{}', -- destinations
  '{}' -- requirements
),
-- order with performer_cp_id and without matching order in db
(  
  'dddddddddddddddddddddddddddddddd', -- id
  '2020-01-01T12:01:00', -- last_event_handled
  '2020-01-01T12:01:00', -- updated
  'moscow', -- zone_id,
  'vip', --tariff_class
  '00000000000000000000000000000000_11111111111111111111111111111111', -- performer_dbid_uuid
  '2020-01-01T12:00:00', -- performer_assigned
  INTERVAL '300 seconds', -- performer_initial_eta
  5000, -- performer_initial_distance
  '2020-01-01T12:00:00', -- first_performer_assigned
  INTERVAL '300 seconds', -- first_performer_initial_eta
  5000, -- first_performer_initial_distance
  0, -- eta_autoreorders_count
  'handle_driving', -- last_event
  '111111111111111111111111', -- user_phone_id
  'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', -- performer_cp_id
  '{20.123123, 30.123123}', -- point_a
  '{}', -- destinations
  '{}' -- requirements
);
