INSERT INTO eats_plus.place_plus_settings
(place_id, active, updated_at)
VALUES
(1, true, '2020-11-25 18:43:00 +03:00'),
(3, true, '2020-11-25 18:43:00 +03:00'),
(4, true, '2020-11-25 18:43:00 +03:00'),
(5, true, '2020-11-25 18:43:00 +03:00'),
(15, false, '2020-11-25 18:43:00 +03:00'),
(52, false, '2020-11-25 18:43:00 +03:00'),
(28, true, '2020-11-25 18:43:00 +03:00'),
(111, true, '2020-11-25 18:43:00 +03:00');

INSERT INTO eats_plus.cashback_settings(
    place_id, cashback, active_from, active_till, type)
VALUES
(1, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(1, 5, '2020-11-25 18:43:00 +03:00', NULL, 'eda'),
(3, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(3, 5, '2020-11-25 18:43:00 +03:00', NULL, 'eda'),
(4, 10, '2020-11-25 18:43:00 +03:00', '2020-12-01 18:43:00 +03:00', 'place'),
(4, 5, '2020-11-25 18:43:00 +03:00', '2020-12-01 18:43:00 +03:00', 'eda'),
(4, 7, '2020-12-01 18:43:00 +03:00', NULL, 'place'),
(5, 10, current_timestamp + '1 day', NULL, 'place'),
(5, 5, current_timestamp + '1 day', NULL, 'eda'),
(15, 15, '2020-11-25 18:43:00 +03:00', '2020-12-01 18:43:00 +03:00', 'place'),
(15, 15, '2020-11-25 18:43:00 +03:00', '2020-12-01 18:43:00 +03:00', 'eda'),
(52, 15, '2020-11-25 18:43:00 +03:00', '2020-12-01 18:43:00 +03:00', 'place'),
(52, 15, '2020-11-25 18:43:00 +03:00', '2020-12-01 18:43:00 +03:00', 'eda'),
(28, 10, '2020-11-25 18:43:00 +03:00', '2020-12-01 18:43:00 +03:00', 'place'),
(28, 5, '2020-11-25 18:43:00 +03:00', '2020-12-01 18:43:00 +03:00', 'eda'),
(111, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(111, 5, '2020-11-25 18:43:00 +03:00', NULL, 'eda'),
(111, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(111, 5, '2020-11-25 18:43:00 +03:00', NULL, 'eda'),
(111, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(111, 5, '2020-11-25 18:43:00 +03:00', NULL, 'eda');