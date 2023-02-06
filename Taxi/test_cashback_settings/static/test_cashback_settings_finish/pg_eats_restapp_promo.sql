INSERT INTO eats_restapp_promo.place_plus_activation
(place_id, status,cashback,starts, ends, updated_at)
VALUES
    ('1', 'active', 5.0, '2020-11-25 18:43:00 +03:00', NULL, current_timestamp),
    ('2', 'active', 6.0, '2020-11-25 18:43:00 +03:00', NULL, current_timestamp),
    ('3', 'active', 7.0, '2020-11-25 18:43:00 +03:00', NULL, current_timestamp),
    ('4', 'active', 3.0, '2021-09-20 18:43:00 +03:00', NULL, current_timestamp),
    ('1', 'active', 10.0, '2021-09-20 18:43:00+00:00', NULL, current_timestamp);

INSERT INTO eats_restapp_promo.active_cashback_settings
(id, place_id, cashback, starts, ends, type, discount_task_id, discount_id)
VALUES
    (1, '1', '5.0', '2020-11-25 18:43:00 +03:00', NULL, 'place', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01', '1230'),
    (2, '1', '5.0', '2020-11-25 18:43:00 +03:00', NULL, 'yandex', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02', '1231'),
    (3, '2', '5.0', '2020-11-25 18:43:00 +03:00', '2021-11-25 18:43:00 +03:00', 'place', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02', '1232'),
    (4, '3', '5.0', '2020-11-25 18:43:00 +03:00', NULL, 'yandex', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa03', NULL);
