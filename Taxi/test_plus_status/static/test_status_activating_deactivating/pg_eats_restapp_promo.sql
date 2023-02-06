INSERT INTO eats_restapp_promo.place_plus_activation
(place_id, status,cashback,starts, ends, updated_at)
VALUES
    ('1', 'activating', 5.0, '2020-11-25 18:43:00 +03:00', NULL, current_timestamp),
    ('2', 'deactivating', 4.4, '2020-11-25 18:43:00 +03:00', NULL, current_timestamp),
    ('3', 'active', 7.0, '2020-11-25 18:43:00 +03:00', NULL, current_timestamp),
    ('3', 'deactivating', 1.0, '2021-12-25 18:43:00 +03:00', NULL, current_timestamp);
