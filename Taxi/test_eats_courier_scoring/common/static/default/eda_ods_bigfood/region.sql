create schema if not exists eda_ods_bigfood;

DROP TABLE IF EXISTS eda_ods_bigfood.region;

create table if not exists eda_ods_bigfood.region
(
    _etl_processed_dttm         timestamp,
    available_flg               boolean,
    billing_subregion_id        bigint,
    bottom_right_lat            numeric,
    bottom_right_lon            numeric,
    bounding_box_left_top_point json,
    center_location_lat         numeric,
    center_location_lon         numeric,
    center_location_point       json,
    country_id                  bigint,
    default_flg                 boolean,
    deleted_flg                 boolean,
    id                          bigint primary key,
    name                        varchar,
    oktmo                       varchar,
    prepositional               varchar,
    region_setting_id           bigint,
    slug                        varchar,
    sort                        bigint,
    timezone                    varchar,
    top_left_lat                numeric,
    top_left_lon                numeric,
    utc_business_dttm           timestamp,
    utc_created_dttm            timestamp,
    utc_deleted_dttm            timestamp,
    utc_updated_dttm            timestamp,
    vox_implant_code            varchar,
    vox_implant_enabled_flg     boolean
);
