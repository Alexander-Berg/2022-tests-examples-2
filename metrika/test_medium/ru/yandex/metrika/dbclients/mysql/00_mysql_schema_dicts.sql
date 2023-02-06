-- DICTS

drop schema if exists dicts;

create schema dicts collate utf8_general_ci;

use dicts;

SET NAMES 'utf8';

create table subscribed_counters
(
    counter_id int(10) unsigned not null primary key
);

create table dynamic_conditions
(
    dyn_cond_id    bigint unsigned not null primary key,
    order_id       bigint unsigned null,
    condition_name varchar(255)    null,
    update_time    bigint unsigned null
);

create table performance_filters
(
    filter_id   bigint        not null primary key,
    order_id    bigint        not null,
    filter_name varchar(1024) null,
    update_time bigint unsigned null
);
