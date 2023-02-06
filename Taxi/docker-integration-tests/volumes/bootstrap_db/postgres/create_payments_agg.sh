#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE dbpaymentsagg;
\connect dbpaymentsagg

CREATE TABLE IF NOT EXISTS "payments_agg_0" (
    id                varchar (40)     not null,
    date_last_change  timestamp        null,
    agg               varchar (40)     not null,
    db                varchar (40)     not null,

    number            serial           not null,
    date              timestamp        not null,
    factor            int              not null,
    group_id          int              not null,
    sum               numeric (18, 6)  not null,
    balance           numeric (18, 6)  not null,
    order_id          varchar (40)     null,
    description       varchar (1024)   not null,
    sum_yandex        numeric (18, 6)  null,
    PRIMARY KEY       (agg,db,id)
);

create index if not exists idx_payments_agg_0_order_id on "payments_agg_0" (order_id nulls last);
create index if not exists idx_payments_agg_0_date on "payments_agg_0" (agg, db, date desc);
create index if not exists idx_payments_agg_0_date_last_change on "payments_agg_0" (date_last_change desc);

