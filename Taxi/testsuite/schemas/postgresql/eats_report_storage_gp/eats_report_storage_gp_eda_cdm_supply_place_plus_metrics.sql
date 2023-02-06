-- Greenplum schemas
CREATE SCHEMA IF NOT EXISTS eda_cdm_supply;

CREATE TABLE eda_cdm_supply.agg_place_plus_metric (
    brand_id BIGINT,
    place_id BIGINT,
    utc_period_start_dttm TIMESTAMP,
    scale_name VARCHAR,
    place_plus_status VARCHAR,
    user_w_plus_gmv_lcy NUMERIC,
    user_wo_plus_gmv_lcy NUMERIC,
    user_w_plus_order_cnt INTEGER,
    user_wo_plus_order_cnt INTEGER,
    cashback_by_place_lcy NUMERIC,
    cashback_spent_by_user_lcy NUMERIC,
    avg_cashback_by_place_pcnt NUMERIC,
    user_w_plus_cashback_topup_order_cnt INT,
    new_user_w_plus_cnt INTEGER,
    new_user_wo_plus_cnt INTEGER,
    user_w_plus_ltv_lcy NUMERIC,
    user_wo_plus_ltv_lcy NUMERIC,
    user_w_plus_frequency_val NUMERIC,
    user_wo_plus_frequency_val NUMERIC,
    _etl_processed_dttm TIMESTAMP
);
