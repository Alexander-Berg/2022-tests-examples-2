INSERT INTO eats_place_rating.place_rating_info(
    place_id,
    cancel_rating, cancel_rating_delta,
    user_rating, user_rating_delta,
    final_rating, final_rating_delta,
    show_rating, calculated_at
) VALUES (1, 3.1, 0.1, 5.0, 0, 4.5, -0.1, true, current_date - interval '12 day'),
         (2, 3.2, 3.2, 5.0, 5.0, 4.6, 4.6, false, current_date - interval '13 day');

INSERT INTO eats_place_rating.greenplum_sync(id, last_known_date, last_sync)
VALUES ('greenplum_cursor', current_date - interval '10 day', current_timestamp)
