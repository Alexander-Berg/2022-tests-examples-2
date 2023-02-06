INSERT INTO eats_place_rating.place_rating_info(
    place_id, cancel_rating, user_rating, final_rating,
    final_rating_delta, user_rating_delta, cancel_rating_delta,
    show_rating, calculated_at
)
VALUES (1, 3.1, 5.0, 4.5, -0.1, 0, -0.1, true, '2020-11-25'::DATE),
       (2, 5, 5, 5, 5, 5, 5, true, '2021-03-04'::DATE),
       (3, 4, 4, 4, 4, 4, 4, false, '2021-03-04'::DATE);

INSERT INTO eats_place_rating.place_cancels_stats
(
    place_id,
    cancel_reason,
    cancel_count,
    calculated_at
)
VALUES (1, 'old reason', 4, current_date),
       (3, 'old reason', 4, current_date);
