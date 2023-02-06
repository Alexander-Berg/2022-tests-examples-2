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

INSERT INTO yt.report_parks_rating_churn_rate (id, park_id, city, date_at,
                                               driver_id, last_order_date)
VALUES (1, '7ad36bc7560449998acbe2c57a75c293', 'Томск', '2021-03-01',
        'a57d409d08a044fc9faab63aca103315', '2021-02-01 00:22:39'),
       (2, '7ad36bc7560449998acbe2c57a75c293', 'Томск', '2021-03-01',
        '284eff9f3524629d5b0eb5a833b7c772', '2021-02-02 08:32:01'),
       (3, '7ad36bc7560449998acbe2c57a75c293', 'Томск', '2021-03-01',
        'fdbb9ae4cec0458b813574f23e65c471', '2021-02-05 22:03:50');
