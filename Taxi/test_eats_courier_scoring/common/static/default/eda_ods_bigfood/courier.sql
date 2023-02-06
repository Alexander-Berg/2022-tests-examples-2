create schema if not exists eda_ods_bigfood;

DROP TABLE IF EXISTS eda_ods_bigfood.courier;

create table if not exists eda_ods_bigfood.courier
(
    _etl_processed_dttm           timestamp,
    admin_id                      bigint,
    api_key                       varchar,
    billing_type                  varchar,
    comment                       varchar,
    courier_service_id            bigint,
    courier_zone_id               bigint,
    id                            bigint primary key,
    last_location_lat             numeric,
    last_location_lon             numeric,
    last_location_point           point,
    order_assign_available_flg    boolean,
    partner_id                    bigint,
    phone_number                  varchar,
    phone_number_raw              varchar,
    region_id                     bigint,
    shift_type                    varchar,
    source                        varchar,
    telegram_chat_id              bigint,
    telegram_name                 varchar,
    type                          varchar,
    username                      varchar,
    utc_blocked_until_dttm        timestamp,
    utc_business_dttm             timestamp,
    utc_courier_zone_updated_dttm timestamp,
    utc_created_dttm              timestamp,
    utc_location_dttm             timestamp,
    utc_logged_out_dttm           timestamp,
    utc_updated_dttm              timestamp,
    work_status                   varchar,
    zendesk_task_id               bigint,
    pool_name                     varchar
);
