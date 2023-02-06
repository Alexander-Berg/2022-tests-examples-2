INSERT INTO eda_cdm_supply.dim_place_rating(
    "_etl_processed_dttm",
    cancel_in_cancel_rating_cnt,
    cancel_rating_val,
    final_rating_val,
    place_id,
    rating_dt,
    show_rating_flg,
    rating_in_user_rating_cnt,
    user_rating_val,
    highest_mark_order_to_improve_user_rating_cnt,
    delivered_order_to_improve_cancel_rating_cnt,
    virtual_rating_in_user_rating_cnt)
VALUES
(
            current_timestamp, 100, 4.4,
            4.8, 10, current_date, true,
            100, 5.0, 10, 11, 120
),
(
            current_timestamp - interval '1 day', 100, 4.5,
            4.9, 10, current_date - interval '1 day', true,
            100, 5.0, 20, NULL, 100
),
(
            current_timestamp - interval '1 day', 100, 4.5,
            4.9, 22, current_date - interval '1 day', true,
            100, 5.0, 20, NULL, 80
),
(
            current_timestamp - interval '8 day', 100, 4.5,
            4.9, 33, current_date - interval '8 day', true,
            100, 5.0, 20, NULL, 60
),
(
            current_timestamp - interval '7 day', 100, 4.5,
            4.9, 33, current_date - interval '7 day', true,
            100, 5.0, 20, NULL, 40
),
(
            current_timestamp - interval '2 day', 100, 4.5,
            4.9, 45, current_date - interval '2 day', true,
            100, 5.0, 20, NULL, 20
),
(
            current_timestamp - interval '30 day', 100, 4.5,
            4.9, 30, current_date - interval '30 day', true,
            100, 5.0, 20, NULL, 10
),
(
            current_timestamp - interval '11 day', 100, 4.5,
            4.9, 22, current_date - interval '11 day', true,
            100, 5.0, 20, NULL, 0
);
