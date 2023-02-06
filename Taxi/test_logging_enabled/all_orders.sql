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
-- new order which has enabled rule:
(
    '1', -- id
    '2020-01-01T12:01:00', -- last_event_handled
    '2020-01-01T12:01:00', -- updated
    'moscow', -- zone_id,
    'econom', --tariff_class
    '00000000000000000000000000000000_11111111111111111111111111111111', -- performer_dbid_uuid
    '2020-01-01T12:00:00', -- performer_assigned
    INTERVAL '300 seconds', -- performer_initial_eta
    5000, -- performer_initial_distance
    '2020-01-01T12:00:00', -- first_performer_assigned
    INTERVAL '300 seconds', -- first_performer_initial_eta
    5000, -- first_performer_initial_distance
    0, -- eta_autoreorders_count
    'handle_driving', -- last_event
    '321', -- user_phone_id
    '{20.123123, 30.123123}', -- point_a
    '{}', -- destinations
    '{}' -- requirements
),
(
    '2', -- id
    '2020-01-01T12:01:00', -- last_event_handled
    '2020-01-01T12:01:00', -- updated
    'spb', -- zone_id,
    'econom', --tariff_class
    '00000000000000000000000000000000_11111111111111111111111111111111', -- performer_dbid_uuid
    '2020-01-01T12:00:00', -- performer_assigned
    INTERVAL '300 seconds', -- performer_initial_eta
    5000, -- performer_initial_distance
    '2020-01-01T12:00:00', -- first_performer_assigned
    INTERVAL '300 seconds', -- first_performer_initial_eta
    5000, -- first_performer_initial_distance
    0, -- eta_autoreorders_count
    'handle_driving', -- last_event
    '321', -- user_phone_id
    '{20.123123, 30.123123}', -- point_a
    '{}', -- destinations
    '{}' -- requirements
),
(
    '3', -- id
    '2020-01-01T12:01:00', -- last_event_handled
    '2020-01-01T12:01:00', -- updated
    'moscow', -- zone_id,
    'comfortplus', --tariff_class
    '00000000000000000000000000000000_11111111111111111111111111111111', -- performer_dbid_uuid
    '2020-01-01T12:00:00', -- performer_assigned
    INTERVAL '300 seconds', -- performer_initial_eta
    5000, -- performer_initial_distance
    '2020-01-01T12:00:00', -- first_performer_assigned
    INTERVAL '300 seconds', -- first_performer_initial_eta
    5000, -- first_performer_initial_distance
    0, -- eta_autoreorders_count
    'handle_driving', -- last_event
    '321', -- user_phone_id
    '{20.123123, 30.123123}', -- point_a
    '{}', -- destinations
    '{}' -- requirements
),
(
    '4', -- id
    '2020-01-01T12:01:00', -- last_event_handled
    '2020-01-01T12:01:00', -- updated
    'moscow', -- zone_id,
    'econom', --tariff_class
    '00000000000000000000000000000000_11111111111111111111111111111111', -- performer_dbid_uuid
    '2020-01-01T12:00:00', -- performer_assigned
    INTERVAL '300 seconds', -- performer_initial_eta
    5000, -- performer_initial_distance
    '2020-01-01T12:00:00', -- first_performer_assigned
    INTERVAL '300 seconds', -- first_performer_initial_eta
    5000, -- first_performer_initial_distance
    0, -- eta_autoreorders_count
    'handle_driving', -- last_event
    '123', -- user_phone_id
    '{37.49133517428459, 55.66009198731399}', -- point_a
    '{{21, 11}}', -- destinations
    '{}' -- requirements
),
(
    '5', -- id
    '2020-01-01T12:01:00', -- last_event_handled
    '2020-01-01T12:01:00', -- updated
    'moscow', -- zone_id,
    'econom', --tariff_class
    '00000000000000000000000000000000_11111111111111111111111111111111', -- performer_dbid_uuid
    '2020-01-01T12:00:00', -- performer_assigned
    INTERVAL '300 seconds', -- performer_initial_eta
    5000, -- performer_initial_distance
    '2020-01-01T12:00:00', -- first_performer_assigned
    INTERVAL '300 seconds', -- first_performer_initial_eta
    5000, -- first_performer_initial_distance
    0, -- eta_autoreorders_count
    'handle_driving', -- last_event
    '321', -- user_phone_id
    '{37.49133517428459, 55.66009198731399}', -- point_a
    '{{21, 11}}', -- destinations
    '{}' -- requirements
);
