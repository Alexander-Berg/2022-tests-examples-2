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
      '100-404', 4, current_timestamp, NULL,
      true
  );


