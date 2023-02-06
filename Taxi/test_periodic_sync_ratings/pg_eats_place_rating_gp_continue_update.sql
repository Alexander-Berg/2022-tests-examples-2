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
    virtual_rating_in_user_rating_cnt
)
VALUES
  (
     current_timestamp, 100, 3.0,
     4.4, 10, current_date, true,
     100, 5.0, NULL, NULL, 120
  ),
  (
     current_timestamp - interval '1 day', 100, 3.1,
     4.5, 10, current_date - interval '1 day', true,
     100, 5.0, NULL, NULL, 100
  ),
  (
     current_timestamp - interval '2 day', 100, 3.2,
     4.6, 10, current_date - interval '2 day', true,
     100, 5.0, NULL, NULL, 80
  );
