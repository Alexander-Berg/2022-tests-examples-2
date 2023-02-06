create schema if not exists eda_ods_bigfood;

DROP TABLE IF EXISTS eda_ods_bigfood.courier_deactivation_reason;

create table if not exists eda_ods_bigfood.courier_deactivation_reason
(
    reason_id bigint primary key,
    _etl_processed_dttm timestamp without time zone,
    alias_code varchar,
    courier_deactivation_reason_group_id bigint,
    reason_name varchar,
    utc_business_dttm timestamp without time zone,
    utc_created_dttm timestamp without time zone,
    utc_deleted_dttm timestamp without time zone,
    utc_updated_dttm timestamp without time zone
);
