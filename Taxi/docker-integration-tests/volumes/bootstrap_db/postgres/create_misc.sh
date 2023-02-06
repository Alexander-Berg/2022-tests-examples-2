#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE dbmisc;

\connect dbmisc

CREATE TABLE "transactions_0" (
    park_id       varchar (32)     not null,
    id            varchar (32)     not null,
    date          timestamp        not null,
    date_last_change timestamp     null,
    pay_id        varchar (32)     not null,
    pay_system    int              not null,
    pay_account   varchar (32)     not null,
    factor        int              not null,
    sum           numeric (18, 6)  not null,
    status        int              not null,
    description   varchar (512)    not null,

    driver_id     varchar (32)     null,
    driver_name   varchar (128)    null,
    driver_signal varchar (32)     null,

    PRIMARY KEY(park_id, id)
);

create index idx_transactions_0_date on "transactions_0" (park_id, date desc);
create index idx_transactions_0_pay_id on "transactions_0" (pay_id);
create index idx_transactions_0_driver_signal on "transactions_0" (park_id, driver_signal asc nulls last);
create index idx_transactions_0_status on "transactions_0" (park_id, status);
create index idx_transactions_0_description on "transactions_0" (park_id, description);

CREATE TABLE "changes_0" (
    park_id     varchar(32)     not null,
    id          varchar(32)     not null,
    date        timestamp       not null,
    object_id   varchar(32)     not null,
    object_type varchar(32)     null,
    user_id     varchar(32)     null,
    user_name   varchar(64)     null,
    counts      int             not null,
    values      varchar(8192)   not null,
    ip          varchar(32)     null,

    PRIMARY KEY(park_id, id)
);

create index idx_changes_0_date on "changes_0" (park_id, date desc);
create index idx_changes_0_object_id on "changes_0" (object_id);
create index idx_changes_0_user_id on "changes_0" (user_id);

CREATE TABLE "feedbacks_0" (
    park_id       varchar (32)     not null,
    id            varchar (32)     not null,
    date          timestamp        not null,
    date_last_change timestamp     null,

    feed_type     int              not null,
    status        int              not null,
    description   varchar (1024)   null,

    score         int              null,

    driver_id     varchar (32)     null,
    driver_name   varchar (128)    null,
    driver_signal varchar (32)     null,

    order_id      varchar (32)     null,
    order_number  int              null,

    user_name     varchar (64)     null,

    PRIMARY KEY(park_id, id)
);

create index idx_feedbacks_0_feed_type on "feedbacks_0" (park_id, feed_type);
create index idx_feedbacks_0_score on "feedbacks_0" (park_id, score nulls last);
create index idx_feedbacks_0_status on "feedbacks_0" (park_id, status);
create index idx_feedbacks_0_driver_id on "feedbacks_0" (driver_id);
create index idx_feedbacks_0_order_id on "feedbacks_0" (order_id nulls last);
create index idx_feedbacks_0_order_number on "feedbacks_0" (park_id, order_number desc nulls last);
create index idx_feedbacks_0_date on "feedbacks_0" (park_id, date desc);
create index idx_feedbacks_0_driver_signal on "feedbacks_0" (park_id, driver_signal asc nulls last);
create index idx_feedbacks_0_user_name on "feedbacks_0" (park_id, user_name);

CREATE TABLE "passengers_0" (
    park_id         varchar (32)     not null,
    id              varchar (32)     not null,
    date            timestamp        not null,
    date_last_change timestamp       null,

    cost_code       varchar (64)     null,

    name            varchar (128)    null,
    count_orders    int              default 0,

    discount_type   int              default 0,
    discount_value  numeric (18, 6)  default 0,
    discount_card   varchar (32)     null,

    address         varchar (512)    null,
    description     varchar (1024)   null,

    PRIMARY KEY (park_id, id)
);

create index idx_passengers_0_date on "passengers_0" (park_id, date desc);
create index idx_passengers_0_name on "passengers_0" (park_id, name nulls last);
create index idx_passengers_0_discount_type on "passengers_0" (park_id, discount_type);
create index idx_passengers_0_discount_card on "passengers_0" (park_id, discount_card nulls last);
create index idx_passengers_0_address on "passengers_0" (park_id, address nulls last);
create index idx_passengers_0_description on "passengers_0" (park_id, description nulls last);
create index idx_passengers_0_cost_code on "passengers_0" (park_id, cost_code nulls last);
EOSQL
