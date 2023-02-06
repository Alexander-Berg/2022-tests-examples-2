INSERT INTO yt.report_parks_rating (id, park_id, city, date_at, bad_marks_value,
                                    new_cars_value, supply_hours_value,
                                    churn_rate_value, bad_marks_points,
                                    new_cars_points, supply_hours_points,
                                    churn_rate_points, total_points,
                                    max_bad_marks_points, max_new_cars_points,
                                    max_supply_hours_points,
                                    max_churn_rate_points, max_total_points,
                                    rank, tier, next_tier_diff_points)
VALUES (1, '7ad36bc7560449998acbe2c57a75c293', 'Томск', '2021-03-01', 135.71,
        64.29, 35.71, 50.00, 285.71, 64.29, 35.71, 50.00, 285.71, 250.00,
        250.00, 250.00, 250.00, 1000.00, 32, 'bronze', 378.58);

INSERT INTO yt.report_parks_rating_new_cars (id, park_id, city, date_at, car_id,
                                             car_price, car_year, is_new_car)
VALUES (1, '7ad36bc7560449998acbe2c57a75c293', 'Томск', '2021-03-01',
        '91866ddc70f74a94a0ff570ea9a08f42', null, null, false),
       (2, '7ad36bc7560449998acbe2c57a75c293', 'Томск', '2021-03-01',
        '91a8158bcd9e4123969c17864b8ec037', 566672.00, 2020, true),
       (3, '7ad36bc7560449998acbe2c57a75c293', 'Томск', '2021-03-01',
        '91a94d67fc8941d5a97be3b6ebd34889', null, 2010, false);
