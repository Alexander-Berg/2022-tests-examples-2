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
    point_a,
    destinations,
    requirements
)
VALUES
-- order for which autoreorder will be called successfully
(
    'order_id1', -- id
    '2020-02-01T12:00:30', -- last_event_handled
    '2020-02-01T12:00:30', -- updated
    'moscow', -- zone_id,
    'econom', --tariff_class
    'dbid_uuid1', -- performer_dbid_uuid
    '2020-02-01T12:00:00', -- performer_assigned
    INTERVAL '200 seconds', -- performer_initial_eta
    5000, -- performer_initial_distance
    '2020-02-01T12:00:00', -- first_performer_assigned
    INTERVAL '200 seconds', -- first_performer_initial_eta
    5000, -- first_performer_initial_distance
    0, -- eta_autoreorders_count
   'handle_driving', -- last_event
   '6141a81573872fb3b53037ed', -- user_phone_id
   '{37.49133517428459, 55.66009198731399}', -- point_a
   '{{21, 11}}', -- destinations
   '{}' -- requirements
),
-- order which has enabled rule but no call autoreorder
-- experiment so autoreorder is not called:
(
    'order_id2', -- id
    '2020-02-01T12:00:30', -- last_event_handled
    '2020-02-01T12:00:30', -- updated
    'ekb', -- zone_id
    'econom', -- tariff_class
    'dbid_uuid1', -- performer_dbid_uuid
    '2020-02-01T12:00:00', -- performer_assigned
    INTERVAL '210 seconds', -- performer_initial_eta
    5000, -- performer_initial_distance
    '2020-02-01T12:00:00', -- first_performer_assigned
    INTERVAL '210 seconds', -- first_performer_initial_eta
    5000, -- first_performer_initial_distance
    0, -- eta_autoreorders_count
   'handle_driving', -- last_event
   '6141a81573872fb3b53037ed', -- user_phone_id
   '{37.49133517428459, 55.66009198731399}', -- point_a
   '{{21, 11}}', -- destinations
   '{}' -- requirements
),
-- order doesn't have enabled rule:
(
    'order_id3', -- id
    '2020-02-01T12:00:30', -- last_event_handled
    '2020-02-01T12:00:30', -- updated
    'moscow', -- zone_id
    'econom', -- tariff_class
    'dbid_uuid1', -- performer_dbid_uuid
    '2020-02-01T12:00:00', -- performer_assigned
    INTERVAL '150 seconds', -- performer_initial_eta
    5000, -- performer_initial_distance
    '2020-02-01T12:00:00', -- first_performer_assigned
    INTERVAL '150 seconds', -- first_performer_initial_eta
    5000, -- first_performer_initial_distance
    0, -- eta_autoreorders_count
   'handle_driving', -- last_event
   '6141a81573872fb3b53037ed', -- user_phone_id
   '{37.49133517428459, 55.66009198731399}', -- point_a
   '{{21, 11}}', -- destinations
   '{}' -- requirements
),
-- order for which autoreorder will be called unsuccessfully
(
    'order_id5', -- id
    '2020-02-01T12:00:30', -- last_event_handled
    '2020-02-01T12:00:30', -- updated
    'moscow', -- zone_id,
    'econom', --tariff_class
    'dbid_uuid1', -- performer_dbid_uuid
    '2020-02-01T12:00:00', -- performer_assigned
    INTERVAL '220 seconds', -- performer_initial_eta
    5000, -- performer_initial_distance
    '2020-02-01T12:00:00', -- first_performer_assigned
    INTERVAL '220 seconds', -- first_performer_initial_eta
    5000, -- first_performer_initial_distance
    0, -- eta_autoreorders_count
   'handle_driving', -- last_event
   '6141a81573872fb3b53037ed', -- user_phone_id
   '{37.49133517428459, 55.66009198731399}', -- point_a
   '{{21, 11}}', -- destinations
   '{}' -- requirements
);
