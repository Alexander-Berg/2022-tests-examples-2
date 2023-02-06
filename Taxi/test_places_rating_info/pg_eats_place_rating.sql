INSERT INTO eats_place_rating.place_rating_info(
    place_id, rating_in_user_rating_count, cancel_rating, user_rating, final_rating,
    final_rating_delta, user_rating_delta, cancel_rating_delta,
    show_rating, calculated_at
) VALUES (1, 6, 3.1, 5.0, 4.5, -0.1, 0, -0.1, true, '2020-11-25'::DATE),
         (1, 5, 3.2, 5.0, 4.6, 4.6, 5.0, 3.2, false, '2020-11-24'::DATE),
         (2, 7, 5, 5, 5, 5, 5, 5, true, '2021-03-04'::DATE),
         (3, null, 4, 4, 4, 4, 4, 4, false, '2021-03-04'::DATE);
