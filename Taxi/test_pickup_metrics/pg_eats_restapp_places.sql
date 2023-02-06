INSERT INTO eats_restapp_places.pickup_status(
    place_id, pickup_started, pickup_enabled, pickup_mode)
VALUES (1, NOW(), true, 'self_allowed'),
       (2, NOW(), false, 'self_allowed'),
       (3, NOW() - INTERVAL '1 DAY', false, 'self_allowed');

INSERT INTO eats_restapp_places.pickup_log(
    uuid, place_id, partner_id, pickup_enabled, created_at)
VALUES ('0', 1, 1, true, NOW()),
       ('1', 2, 2, false, NOW()),
       ('2', 3, 3, true, NOW() - INTERVAL '1 DAY'),
       ('3', 4, 4, false, NOW() - INTERVAL '1 DAY');
