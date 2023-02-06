INSERT INTO eats_plus.place_plus_settings
    (place_id, active, updated_at)
VALUES
(1, true, '2020-11-25 18:43:00 +03:00'),
(8, true, '2020-11-25 18:43:00 +03:00'),
(45, true, '2020-11-25 18:43:00 +03:00'),
(78, true, '2020-11-25 18:43:00 +03:00');

INSERT INTO eats_plus.cashback_settings(place_id,cashback,active_from,type)
VALUES
(1, 10, '2020-11-25 18:43:00 +03:00', 'place'),
(1, 5, '2020-11-25 18:43:00 +03:00', 'eda'),
(8, 10, '2020-11-25 18:43:00 +03:00', 'place'),
(45, 10, '2020-11-25 18:43:00 +03:00', 'place'),
(45, 10, '2020-11-25 18:43:00 +03:00', 'eda'),
(78, 5, '2020-11-25 18:43:00 +03:00', 'place'),
(78, 5, '2020-11-25 18:43:00 +03:00', 'eda');

INSERT INTO eats_plus.user_info
(yandex_uid, eater_id, has_orders)
VALUES
('3456723', 'eater-3456723', true),
('3456722', 'eater-3456722', false),
('3456726', 'eater-3456726', false);
