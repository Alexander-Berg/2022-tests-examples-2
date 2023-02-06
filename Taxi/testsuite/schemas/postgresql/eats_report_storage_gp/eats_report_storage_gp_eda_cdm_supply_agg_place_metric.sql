-- Greenplum schemas
CREATE SCHEMA IF NOT EXISTS eda_cdm_supply;

CREATE TABLE eda_cdm_supply.agg_place_metric (
    place_id                BIGINT,
    msk_period_start_dttm   TIMESTAMP,
    scale_name              VARCHAR,
    brand_id                BIGINT,
    delivery_type           VARCHAR,
    region_name             VARCHAR,
    order_cancel_cnt        BIGINT,
    order_success_cnt       BIGINT,
    order_cnt               BIGINT,
    order_cancel_pcnt       NUMERIC,
    revenue_earned_lcy      NUMERIC,
    revenue_lost_lcy        NUMERIC,
    revenue_lcy             NUMERIC,
    revenue_average_lcy     NUMERIC,
    place_address           TEXT,
    currency_code           VARCHAR,
    place_availability_pcnt NUMERIC,
    order_per_place_avg     NUMERIC,
    plan_work_time_min      BIGINT,
    fact_work_time_min      BIGINT,
    _etl_processed_dttm     TIMESTAMP
);
