insert into eda_cdm_supply.v_fct_place_cancel_reason_count_act
(
    place_id,
    place_cancel_reason_name,
    place_cancel_cnt,
    rating_dt)
VALUES
(
    1, 'reason 1', 4, current_date
),
(
    11, 'reason 1', 4, current_date
),
(
    12, 'reason 1', 4, current_date
),
(
    13, 'reason 1', 4, current_date
),
(
    2, 'reason 2', 6, current_date
),
(
    2, 'reason 1', 13, current_date
),
(
    21, 'reason 1', 1, current_date
),
(
    4, 'reason 3', 10, current_date
);

insert into eda_cdm_supply.fct_place_user_rating_orders_act
(
    _etl_processed_dttm,
    msk_feedback_filled_dttm,
    msk_order_dttm,
    order_nr,
    place_id,
    rating_dt,
    rating_val,
    rating_weight_val)
VALUES
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-200', 1, current_timestamp, 5,
            200
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-204', 1, current_timestamp, 5,
            200
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-404', 1, current_timestamp, 5,
            200
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-404', 31, current_timestamp, 5,
            200
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-404', 32, current_timestamp, 5,
            200
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-404', 33, current_timestamp, 5,
            200
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-300', 2, current_timestamp, 4,
            150
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-404', 4, current_timestamp, 3,
            100
);

insert into eda_cdm_supply.fct_place_cancel_rating_orders_act
(
    _etl_processed_dttm,
    msk_final_dttm,
    msk_order_dttm,
    order_nr,
    place_id,
    rating_dt,
    place_cancel_reason_name,
    place_cancel_flg)
VALUES
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-200', 1, current_timestamp, 'reason for 100-200',
            true
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-300', 2, current_timestamp, NULL,
            true
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-404', 2, current_timestamp, NULL,
            true
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-500', 2, current_timestamp, NULL,
            true
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-300', 22, current_timestamp, NULL,
            true
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-404', 22, current_timestamp, NULL,
            true
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-300', 23, current_timestamp, NULL,
            true
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-300', 24, current_timestamp, NULL,
            true
),
(
            current_timestamp, current_timestamp, current_timestamp,
            '100-404', 4, current_timestamp, NULL,
            true
);

insert into eda_cdm_supply.v_fct_place_predefined_comment_count_act
(
    place_id,
    predefined_comment,
    predefined_comment_cnt,
    predefined_comment_type,
    rating_dt)
VALUES
(
    1, 'predefined comment 1', 4, 'dislike', current_date
),
(
    1, 'predefined comment 2', 4, 'dislike', current_date
),
(
    1, 'predefined comment 3', 4, 'dislike', current_date
),
(
    41, 'predefined comment 1', 4, 'dislike', current_date
),
(
    42, 'predefined comment 2', 4, 'dislike', current_date
),
(
    42, 'predefined comment 1', 4, 'dislike', current_date
),
(
    43, 'predefined comment 1', 4, 'dislike', current_date
),
(
    44, 'predefined comment 1', 4, 'dislike', current_date
),
(
    44, 'predefined comment 3', 4, 'dislike', current_date
),
(
    2, 'predefined comment 2', 6, 'like', current_date
),
(
    4, 'predefined comment 4', 10, 'like', current_date
);
