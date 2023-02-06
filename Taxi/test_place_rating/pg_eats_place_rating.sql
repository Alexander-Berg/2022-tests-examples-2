INSERT INTO eats_place_rating.place_rating_info(
    place_id, cancel_rating, user_rating, final_rating,
    final_rating_delta, user_rating_delta, cancel_rating_delta,
    show_rating, calculated_at, highest_mark_order_to_improve_user_rating_count,
    virtual_rating_in_user_rating_count, order_in_cancel_rating_count, cancel_in_cancel_rating_count
) VALUES
         (5, 4.0, 3.5, 4.5, -0.1, 0, -0.1, true, '2021-04-20'::DATE, 3, 4, 220, 2),
         (5, 3.9, 3.5, 4.5, -0.1, 0, -0.1, true, '2021-04-19'::DATE, 3, 4, 200, 0),
         (5, 3.8, 3.5, 4.5, -0.1, 0, -0.1, true, '2021-04-18'::DATE, 3, 4, 200, 3),
         (5, 3.7, 3.5, 4.5, -0.1, 0, -0.1, true, '2021-04-17'::DATE, 3, 4, 200, 0),
         (5, 3.8, 3.5, 4.5, -0.1, 0, -0.1, true, '2021-04-16'::DATE, 3, 4, 180, 0),
         (5, 3.7, 3.5, 4.5, -0.1, 0, -0.1, true, '2021-04-15'::DATE, 3, 4, 160, 1),
         (5, 3.8, 3.5, 4.5, -0.1, 0, -0.1, true, '2021-04-14'::DATE, 3, 4, 140, 0),
         (5, 3.6, 3.5, 4.5, -0.1, 0, -0.1, true, '2021-04-13'::DATE, 3, 4, 120, 0),
         (5, 4.0, 3.5, 4.5, -0.1, 0, -0.1, true, '2021-03-04'::DATE, 3, 4, 100, 0),
         (7, 4, 4, 4, 4, 4, 4, false, current_date, 5, 3, 0, 0),
         (8, 2, 2, 3, 4, 4, 4, false, current_date, 5, 3, 0, 0),
         (9, 4, 4, 3, 4, 4, 4, false, current_date, 5, 3, 0, 0),
         (10, 4, 4, 3, 4, 4, 4, false, current_date, 5, 3, 0, 0);

INSERT INTO eats_place_rating.feedback_weight
(
    place_id,
    order_nr,
    rating,
    rating_weight,
    feedback_created_at,
    order_created_at,
    rating_dt,
    updated_at
) VALUES (5, '100-200', 5, 200, '2021-04-13 00:00+00'::TIMESTAMP, current_timestamp, '2021-04-13'::DATE, current_timestamp),
         (5, '100-100', 2, 199, '2021-04-12 00:00+00'::TIMESTAMP, current_timestamp, '2021-04-12'::DATE, current_timestamp),
         (5, '100-120', 2, 199, '2021-04-12 00:00+00'::TIMESTAMP, current_timestamp, NULL, current_timestamp);

INSERT INTO eats_place_rating.predefined_comments_stats
(
    place_id,
    predefined_comment,
    comments_count,
    comment_type,
    calculated_at
) VALUES (7, 'old comment', 4, 'dislike', current_date),
         (10, 'comment_1', 4, 'dislike', current_date);

INSERT INTO eats_place_rating.place_cancels_stats
(
    place_id,
    cancel_reason,
    cancel_count,
    calculated_at
) VALUES (10, 'reason_1', 4, current_date);
