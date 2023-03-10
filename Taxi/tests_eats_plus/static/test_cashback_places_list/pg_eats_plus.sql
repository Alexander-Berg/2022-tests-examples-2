INSERT INTO eats_plus.place_plus_settings
(place_id, active, updated_at)
VALUES
(1, true, '2020-11-25 18:43:00 +03:00'),
(2, true, '2020-11-25 18:43:00 +03:00'),
(3, true, '2020-11-25 18:43:00 +03:00'),
(4, true, '2020-11-25 18:43:00 +03:00'),
(5, false, '2020-11-25 18:43:00 +03:00'),
(6, true, '2020-11-25 18:43:00 +03:00'),
(45, true, '2020-11-25 18:43:00 +03:00'),
(78, true, '2020-11-25 18:43:00 +03:00');

INSERT INTO eats_plus.cashback_settings(place_id,cashback,active_from,active_till,type)
VALUES
(1, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(1, 5, '2020-11-25 18:43:00 +03:00', NULL, 'eda'),
(2, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(3, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(4, 5, '2020-11-25 18:43:00 +03:00',NULL, 'eda'),
(5, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(5, 5, '2020-11-25 18:43:00 +03:00', NULL, 'eda'),
(6, 10, '2021-11-25 18:43:00 +03:00', NULL, 'place'),
(6, 5, '2021-11-25 18:43:00 +03:00', NULL, 'eda'),
(45, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(45, 10, '2020-11-25 18:43:00 +03:00', NULL, 'eda'),
(78, 5, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(78, 5, '2020-11-25 18:43:00 +03:00', NULL, 'eda');

INSERT INTO eats_plus.user_info
(yandex_uid, eater_id, has_orders)
VALUES
('3456723', 'eater-3456723', true),
('3456722', 'eater-3456722', false),
('3456726', 'eater-3456726', false);
