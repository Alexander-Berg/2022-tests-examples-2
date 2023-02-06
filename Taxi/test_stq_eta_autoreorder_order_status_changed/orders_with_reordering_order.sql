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
  autoreorder_in_progress,
  reorder_situation_detected,
  last_event,
  user_phone_id,
  point_a,
  destinations,
  requirements
)
VALUES
(
  'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', -- id
  '2020-01-01T12:01:00', -- last_event_handled
  '2020-01-01T12:01:00', -- updated
  'moscow', -- zone_id,
  'vip', --tariff_class
  '33333333333333333333333333333333_22222222222222222222222222222222', -- performer_dbid_uuid   
  '2020-01-01T12:00:00', -- performer_assigned
  INTERVAL '300 seconds', -- performer_initial_eta
  5000, -- performer_initial_distance
  '2020-01-01T12:00:00', -- first_performer_assigned
  INTERVAL '300 seconds', -- first_performer_initial_eta
  5000, -- first_performer_initial_distance
  0, -- eta_autoreorders_count
  true, -- autoreorder_in_progress
  true, -- reorder_situation_detected
  'handle_driving', -- last_event
  '6141a81573872fb3b53037ed', -- user_phone_id
  '{37.49133517428459, 55.66009198731399}', -- point_a
  '{{21, 11}}', -- destinations
  '{}' -- requirements
);
