#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE dbfeedbacks;
\connect dbfeedbacks

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

