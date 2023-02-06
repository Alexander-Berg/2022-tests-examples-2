-- Greenplum schemas
CREATE SCHEMA IF NOT EXISTS eda_cdm_supply;

CREATE TABLE eda_cdm_supply.dim_place_rating
(
    _etl_processed_dttm timestamp,
    cancel_in_cancel_rating_cnt integer,
    cancel_rating_val numeric,
    final_rating_val numeric,
    place_id integer,
    rating_dt date,
    show_rating_flg boolean,
    rating_in_user_rating_cnt integer,
    user_rating_val numeric,
    highest_mark_order_to_improve_user_rating_cnt integer,
    delivered_order_to_improve_cancel_rating_cnt integer,
    virtual_rating_in_user_rating_cnt integer,
    order_in_cancel_rating_cnt integer
);

create table eda_cdm_supply.fct_place_user_rating_orders_act
(
    _etl_processed_dttm timestamp,
    msk_feedback_filled_dttm timestamp,
    msk_order_dttm timestamp,
    order_nr text,
    place_id bigint,
    rating_dt date,
    rating_val bigint,
    rating_weight_val bigint
);

create table eda_cdm_supply.fct_place_cancel_rating_orders_act
(
    place_id bigint,
    order_nr text,
    place_cancel_flg boolean,
    place_cancel_reason_name text,
    rating_dt date,
    msk_order_dttm timestamp,
    msk_final_dttm timestamp,
    _etl_processed_dttm timestamp
);

create table eda_cdm_supply.v_fct_place_predefined_comment_count_act
(
    place_id bigint,
    predefined_comment text,
    predefined_comment_cnt integer,
    predefined_comment_type text,
    rating_dt date
);

create table eda_cdm_supply.v_fct_place_cancel_reason_count_act
(
    place_id bigint,
    place_cancel_reason_name text,
    place_cancel_cnt integer,
    rating_dt date
);
