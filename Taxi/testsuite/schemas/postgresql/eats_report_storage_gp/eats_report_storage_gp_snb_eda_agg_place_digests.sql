-- Greenplum schemas
CREATE SCHEMA IF NOT EXISTS snb_eda;

CREATE TABLE IF NOT EXISTS snb_eda.agg_place_digests (
    place_id                         BIGINT NOT NULL,
    period_date                      DATE NOT NULL,
    place_name                       TEXT,
    place_address                    TEXT,
    delivery_type                    TEXT,
    currency_code                    TEXT,
    orders_total_cnt                 INTEGER,
    orders_total_delta_cnt           INTEGER,
    orders_success_cnt               INTEGER,
    orders_success_delta_cnt         INTEGER,
    revenue_earned_lcy               NUMERIC,
    revenue_earned_delta_lcy         NUMERIC,
    revenue_lost_lcy                 NUMERIC,
    revenue_lost_delta_lcy           NUMERIC,
    fines_lcy                        NUMERIC,
    fines_delta_lcy                  NUMERIC,
    delay_min                        INTEGER,
    delay_delta_min                  INTEGER,
    rating                           NUMERIC,
    rating_delta                     NUMERIC,
    fact_work_time_min               INTEGER,
    fact_work_time_delta_min         INTEGER,
    plan_work_time_min               INTEGER,
    plan_work_time_delta_min         INTEGER,
    _etl_updated_at                  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (place_id, period_date)
);
