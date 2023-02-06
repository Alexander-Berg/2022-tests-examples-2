INSERT INTO eats_report_storage.rad_suggests (place_id, prioriy, suggest)
VALUES (1, 1, 'more_photos'),
       (1, 3, 'dish_as_gift_flg'),
       (1, 5, 'discount_flg'),
       (1, 4, 'second_for_free_flg'),
       (2, 5, 'low_rating'),
       (2, 3, 'more_photos'),
       (2, 2, 'discount_flg'),
       (2, 1, 'second_for_free_flg'),
       (3, 0.5, 'low_rating'),
       (3, 1.2, 'more_photos'),
       (4, 0.01, 'low_rating'),
       (4, 0.2, 'more_photos'),
       (5, 6, 'low_cancel_rating');

INSERT INTO eats_report_storage.rad_quality (place_id, brand_id, name, address, rating, orders,
                                             avg_check, cancel_rating, pict_share, plus_flg, dish_as_gift_flg,
                                             discount_flg, second_for_free_flg, pickup_flg, mercury_flg)
VALUES (1, 1, 'Burgers', 'Moon', 4.4, 10, 10.5, 2.4, 10.5, false, true, false, false, false, true),
       (2, 20, 'Burgers2', 'Moon2', 3.4, 10, 10.5, 2.4, 10.5, false, false, false, true, false, true),
       (3, 30, 'Burgers3', 'Moon3', 2.4, 10, 10.5, 2.5, 10.5, false, false, false, false, false, true),
       (4, 40, 'Burgers4', 'Moon4', 4.4, 10, 2.5, 2.4, 4.5, false, false, false, false, false, true),
       (5, 50, 'Burgers4', 'Moon4', 4.4, 10, 2.5, 2.4, 4.5, false, false, false, false, false, true);
