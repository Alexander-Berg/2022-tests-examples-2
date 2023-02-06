-- Greenplum schemas
CREATE SCHEMA IF NOT EXISTS eda_cdm_supply;

CREATE TABLE eda_cdm_supply.agg_place_promo_metric (
    place_id BIGINT,
    msk_period_start_dttm TIMESTAMP,
    scale_name VARCHAR,
    brand_id INT,
    delivery_type VARCHAR,
    promo_id BIGINT,
    promo_type_id BIGINT,
    place_revenue_lcy NUMERIC,
    place_lost_revenue_lcy NUMERIC,
    successful_order_cnt INT,
    order_cancelled_by_place_cnt INT,
    new_user_cnt INT,
    discount_for_item_list_cnt INT,
    one_plus_one_cnt INT,
    conversion_to_order_pcnt NUMERIC,
    unique_user_visit_cnt INT,
    user_w_order_cnt INT,
    average_order_cost_lcy NUMERIC,
    _etl_processed_dttm TIMESTAMP
);
