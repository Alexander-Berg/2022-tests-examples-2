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
      '100-300', 2, current_timestamp, 4,
      150
  ),
  (
      current_timestamp, current_timestamp, current_timestamp,
      '100-404', 4, current_timestamp, 3,
      100
  );
