insert into eda_cdm_supply.v_fct_place_cancel_reason_count_act
(
    place_id,
    place_cancel_reason_name,
    place_cancel_cnt,
    rating_dt
)
VALUES (1, 'reason 1', 4, current_date),
       (2, 'reason 2', 6, current_date),
       (4, 'reason 3', 10, current_date);
