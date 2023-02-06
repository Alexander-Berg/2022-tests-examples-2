CREATE SCHEMA IF NOT EXISTS eda_cdm_quality;

DROP TABLE IF EXISTS eda_cdm_quality.fct_executor_fault;

CREATE TABLE IF NOT EXISTS eda_cdm_quality.fct_executor_fault
(
    order_id                     integer,
    order_nr                     varchar,
    lcl_defect_dttm              timestamp,
    our_refund_total_lcy         numeric,
    incentive_refunds_lcy        numeric,
    incentive_rejected_order_lcy numeric,
    courier_id                   bigint,
    executor_profile_id          varchar,
    park_taximeter_id            varchar,
    defect_type                  text,
    crm_comment                  text
);
