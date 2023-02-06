create schema if not exists eda_ods_bigfood;

DROP TABLE IF EXISTS eda_ods_bigfood.courier_deactivation_info;

create table if not exists eda_ods_bigfood.courier_deactivation_info
(
    courier_deactivation_id bigint primary key,
    _etl_processed_dttm timestamp without time zone,
    courier_deactivation_reason_id bigint,
    courier_id bigint,
    deactivation_reason_comment varchar,
    utc_business_dttm timestamp without time zone,
    utc_created_dttm timestamp without time zone,
    utc_updated_dttm timestamp without time zone
);
