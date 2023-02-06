INSERT INTO eats_plus.plus_settings_change_history
(id, place_id, active, place_active_from)
VALUES
(1, 1, true, '2020-11-01 10:10:00 +03:00'),
(2, 2, true, '2020-11-22 10:10:00 +03:00'),
(4, 2, true, '2020-11-02 10:10:00 +03:00'),
(3, 2, false, '2020-11-12 10:10:00 +03:00'),
(5, 4, false, NULL);


INSERT INTO eats_plus.place_plus_settings
(place_id, active, updated_at)
VALUES
(1, false, '2020-11-25 10:10:00 +03:00'),
(2, true, '2020-11-25 10:10:00 +03:00');


INSERT INTO eats_plus.cashback_settings(
    place_id, cashback, active_from, active_till, type)
VALUES
(1, 10, '2020-11-25 10:10:00 +03:00', NULL, 'place'),
(1, 5, '2020-11-25 10:10:00 +03:00', NULL, 'eda'),
(2, 12, '2020-11-25 10:10:00 +03:00', NULL, 'place'),
(2, 5, '2020-11-25 10:10:00 +03:00', NULL, 'eda');
