INSERT INTO eats_place_rating.place_rating_info(
    place_id, cancel_rating, user_rating, final_rating,
    final_rating_delta, user_rating_delta, cancel_rating_delta,
    show_rating, calculated_at
) VALUES (1, 3.1, 5.0, 4.5, -0.1, 0, -0.1, true, '2020-11-25'::DATE),
         (2, 5, 5, 5, 5, 5, 5, true, '2021-03-04'::DATE),
         (3, 4, 4, 4, 4, 4, 4, false, '2021-03-04'::DATE);

INSERT INTO eats_place_rating.feedback_weight
(
    place_id,
    order_nr,
    rating,
    rating_weight,
    feedback_created_at,
    order_created_at,
    calculated_at,
    updated_at
) VALUES (1, '100-100', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp-interval '25 hours'),
         (2, '100-400', 2, 1, current_timestamp, current_timestamp, current_timestamp, current_timestamp-interval '25 hours'),
         (4, '100-100', 5, 200, current_timestamp, current_timestamp, current_timestamp, current_timestamp),
         (7, '100-400', 2, 1, current_timestamp, current_timestamp, current_timestamp, current_timestamp);
