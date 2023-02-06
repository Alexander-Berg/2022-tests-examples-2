-- Greenplum schemas
CREATE SCHEMA IF NOT EXISTS snb_eda;

CREATE TABLE snb_eda.rad_dm_client_metric (
    place_id                         BIGINT,
    brand_id                         BIGINT,
    utc_period_start_dttm            TIMESTAMP,
    scale_name                       VARCHAR,
    users_with_1_order_cnt           INT,
    users_with_2_orders_cnt          INT,
    users_with_3_orders_and_more_cnt INT,
    unique_users_cnt                 INT,
    newcommers_cnt                   INT,
    oldcommers_cnt                   INT,
    oldcommers_gmv_pcnt              NUMERIC,
    oldcommers_gmv_lcy               NUMERIC,
    newcommers_gmv_lcy               NUMERIC,
    _etl_processed_dttm              TIMESTAMP
);
