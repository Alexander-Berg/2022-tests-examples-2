create schema if not exists taxi_ods_dbdrivers;

DROP TABLE IF EXISTS taxi_ods_dbdrivers.executor_profile;

create table if not exists taxi_ods_dbdrivers.executor_profile
(
    _etl_processed_dttm                timestamp,
    address                            varchar,
    appmetrica_uuid                    varchar,
    balance_deny_onlycard_flg          boolean,
    bigfood_courier_id                 bigint,
    car_profile_id                     varchar,
    deaf_flg                           boolean,
    driver_license_birth_dt            date,
    driver_license_country_name        varchar,
    driver_license_expire_dt           date,
    driver_license_id                  varchar,
    driver_license_issue_dt            date,
    driver_license_pd_id               varchar,
    driver_license_raw_id              varchar,
    email_pd_id                        varchar,
    executor_profile_id                varchar,
    first_name                         varchar,
    full_name                          varchar,
    hiring_source_code                 varchar,
    hiring_type_code                   varchar,
    last_name                          varchar,
    license_experience_start_dt        date,
    middle_name                        varchar,
    own_terminal_flg                   boolean,
    park_taximeter_id                  varchar,
    phone_pd_id_list                   character varying[],
    provider_code_list                 character varying[],
    tax_identification_number_pd_id    varchar,
    taximeter_locale_code              varchar,
    taximeter_version_code             varchar,
    utc_created_dttm                   timestamp,
    utc_fired_dttm                     timestamp,
    utc_hired_dttm                     timestamp,
    utc_hiring_rule_end_dttm           timestamp,
    utc_modified_dttm                  timestamp,
    work_status_code                   varchar,
    taxi_available_flg                 boolean,
    lavka_available_flg                boolean,
    eda_available_flg                  boolean,
    taxi_walking_courier_available_flg boolean
);

CREATE UNIQUE INDEX IF NOT EXISTS taxi_ods_dbdrivers_executor_profile_id
    ON taxi_ods_dbdrivers.executor_profile (executor_profile_id, park_taximeter_id);
