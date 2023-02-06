#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE dbpayments;

\connect dbpayments

CREATE TABLE "payments_0" (
    park_id       varchar (32)     not null,
    id            varchar (40)     not null,
    number        serial           not null,
    date          timestamp        not null,

    factor        int              not null,
    payment       int              not null,
    group_id      int              not null,
    groups        varchar (128)    null,

    sum           numeric (18, 6)  not null,
    balance       numeric (18, 6)  not null,

    driver_id     varchar (32)     not null,
    driver_name   varchar (128)    null,
    driver_signal varchar (32)     null,

    order_id      varchar (32)     null,
    order_number  int              null,
    description   varchar (1024)   not null,

    slip          varchar (36)     null,
    user_name     varchar (64)     null,

    date_last_change timestamp     not null,

    PRIMARY KEY(park_id, id)
);

create index idx_payments_0_driver_id on "payments_0" (park_id, driver_id);

create index idx_payments_0_order_id on "payments_0" (park_id, order_id nulls last);

create index idx_payments_0_date on "payments_0" (date desc);

create index idx_payments_0_group_id on "payments_0" (group_id); --можно удалить после переезда отчётов в YT

create index idx_payments_0_park_id_factor_groups on "payments_0" (park_id, factor, upper(groups COLLATE "en_US")); --можно удалить после переезда отчётов в YT

create index idx_payments_0_payment on "payments_0" (payment); --можно удалить после переезда отчётов в YT

create index idx_payments_0_date_last_change on "payments_0" (date_last_change desc);
EOSQL
