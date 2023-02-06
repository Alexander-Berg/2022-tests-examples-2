create schema if not exists eda_ods_bigfood;

DROP TABLE IF EXISTS eda_ods_bigfood.place_delivery_zone;

create table if not exists eda_ods_bigfood.place_delivery_zone
(
    _etl_processed_dttm               timestamp,
    courier_type                      varchar,
    delivery_condition_id             bigint,
    marketplace_delivery_time_mnt_avg bigint,
    place_delivery_zone_id            bigint primary key,
    place_delivery_zone_name          varchar,
    place_delivery_zone_type          varchar,
    place_id                          bigint,
    shipping_type                     varchar,
    synced_schedule_flg               boolean,
    time_of_arrival_mnt               bigint,
    utc_business_dttm                 timestamp,
    utc_created_dttm                  timestamp,
    utc_deactivated_dttm              timestamp,
    utc_updated_dttm                  timestamp,
    enabled_flg                       boolean
);
