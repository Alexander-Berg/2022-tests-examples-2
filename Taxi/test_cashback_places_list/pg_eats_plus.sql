INSERT INTO eats_plus.place_plus_settings
(place_id, active, updated_at)
VALUES
(1, true, '2020-11-25 18:43:00 +03:00'),
(2, true, '2020-11-25 18:43:00 +03:00'),
(3, true, '2020-11-25 18:43:00 +03:00');

INSERT INTO eats_plus.cashback_settings(place_id,cashback,active_from,active_till,type)
VALUES
(1, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place'),
(1, 5, '2020-11-25 18:43:00 +03:00', NULL, 'eda'),
(2, 10, '2020-11-25 18:43:00 +03:00', NULL, 'place');
