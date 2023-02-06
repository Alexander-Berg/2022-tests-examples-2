create schema if not exists eda_ods_bigfood;

DROP TABLE IF EXISTS eda_ods_bigfood.courier_meta_data;

create table if not exists eda_ods_bigfood.courier_meta_data
(
    _etl_processed_dttm                        timestamp,
    courier_id                                 bigint primary key,
    deactivation_initiator_name                varchar,
    deaf_mute_flg                              boolean,
    dedicated_courier_flg                      boolean,
    dedicated_picker_flg                       boolean,
    fixed_shifts_option_enabled_flg            boolean,
    has_health_card_flg                        boolean,
    has_own_bicycle_flg                        boolean,
    has_terminal_for_payment_on_site_flg       boolean,
    last_app_version_code                      varchar,
    logistic_place_group_id                    bigint,
    park_courier_flg                           boolean,
    picker_flg                                 boolean,
    rover_flg                                  boolean,
    storekeeper_flg                            boolean,
    uniform_returned_flg                       boolean,
    utc_business_dttm                          timestamp,
    utc_created_dttm                           timestamp,
    utc_fixed_shifts_option_enabled_since_dttm timestamp,
    utc_updated_dttm                           timestamp
)
