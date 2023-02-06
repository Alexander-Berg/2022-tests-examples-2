INSERT INTO eats_restapp_promo.place_plus_activation
(place_id, status,cashback,starts, ends, updated_at)
VALUES
    ('123', 'active', 5.0, '2020-11-25 18:43:00 +03:00', NULL, current_timestamp);

INSERT INTO eats_restapp_promo.active_cashback_settings
(place_id, cashback, starts, ends, type, discount_task_id, discount_id)
VALUES
    ('123', '5.0', current_timestamp - interval '10 day', NULL, 'place', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01', '1230'),
    ('123', '5.0', current_timestamp - interval '10 day', NULL, 'yandex', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02', '1231');
