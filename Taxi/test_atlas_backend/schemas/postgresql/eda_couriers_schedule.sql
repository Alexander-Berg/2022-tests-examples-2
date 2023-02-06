create schema if not exists eda_couriers_schedule;

BEGIN;

create type courier_type as enum ('pedestrian', 'bicycle', 'vehicle');
create type courier_work_status as enum ('active', 'blocked', 'on_vacation', 'ill', 'deactivated', 'lost', 'inactive', 'candidate');
create type courier_service as enum ('eats', 'driver-profiles');

create table couriers
(
    id                                       integer                                not null
        constraint couriers_pkey
            primary key,
    group_id                                 integer,
    region_id                                integer                                not null,
    courier_type                             courier_type                           not null,
    name                                     varchar(255)                           not null,
    work_status                              courier_work_status                    not null,
    created_at                               timestamp(0)                           not null,
    updated_at                               timestamp(0) default CURRENT_TIMESTAMP not null,
    service                                  courier_service                        not null,
    external_id                              varchar(255) default NULL::character varying,
    pool_name                                varchar(255) default NULL::character varying,
    logistics_group_id                       integer,
    birthday                                 date,
    is_storekeeper                           boolean      default false             not null,
    is_dedicated_picker                      boolean      default false             not null,
    is_picker                                boolean      default false             not null,
    use_logistics_group_for_unplanned_shifts boolean      default false             not null,
    is_park_courier                          boolean      default false             not null,
    is_rover                                 boolean      default false             not null,
    is_fixed_shifts_option_enabled           boolean      default false             not null
);


create type shift_pool as enum ('courier', 'storekeeper', 'dedicated_picker', 'picker', 'park_courier');
create type shift_service as enum ('eda', 'lavka', 'shop', 'scooter');
create type shift_status as enum ('planned', 'in_progress', 'on_pause', 'closed', 'not_started', 'draft', 'deleted', 'scheduled_pause');
create type shift_type as enum ('planned', 'planned-extra', 'replacement', 'unplanned', 'fixed');

create sequence analytics_timetable_seq;


create table courier_shifts
(
    id                           bigint         default nextval('analytics_timetable_seq'::regclass) not null
        constraint courier_shifts_pkey
            primary key,
    courier_offline_time         integer                                                             not null,
    courier_id                   integer,
    updated_at                   timestamp(0)   default CURRENT_TIMESTAMP                            not null,
    status                       shift_status   default 'planned'::shift_status                      not null,
    has_lateness                 boolean        default false                                        not null,
    has_early_leaving            boolean        default false                                        not null,
    is_abandoned                 boolean        default false                                        not null,
    region_id                    integer,
    zone_id                      integer,
    start_time                   timestamp(0)   default NULL::timestamp without time zone,
    end_time                     timestamp(0)   default NULL::timestamp without time zone,
    date                         date,
    courier_type                 integer,
    parent_id                    bigint,
    courier_assigned_at          timestamp(0)   default NULL::timestamp without time zone,
    created_at                   timestamp(0)   default now(),
    mass_upload_id               integer,
    type                         shift_type,
    external_id                  varchar(128)   default NULL::character varying,
    is_zone_checked              boolean        default true                                         not null,
    guarantee                    numeric(13, 2) default NULL::numeric,
    pool                         shift_pool     default 'courier'::shift_pool                        not null,
    logistics_group_id           integer,
    effective_logistics_group_id integer,
    start_location_id            bigint,
    service                      shift_service
);

create table courier_shift_states
(
    id             bigserial                              not null
        constraint courier_shift_states_pkey
            primary key,
    shift_id       bigint                                 not null,
    started_at     timestamp(0)                           not null,
    finished_at    timestamp(0) default NULL::timestamp without time zone,
    duration       integer,
    updated_at     timestamp(0) default CURRENT_TIMESTAMP not null,
    pause_duration integer,
    created_at     timestamp(0) default CURRENT_TIMESTAMP not null
);

create type courier_state_type as enum ('online', 'offline', 'logged out');

create table courier_states
(
    courier_id             integer                    not null
        constraint courier_states_pkey
            primary key,
    state                  courier_state_type         not null,
    updated_at             timestamp(0)               not null,
    last_online            timestamp(0) default NULL::timestamp without time zone,
    is_busy                boolean      default false not null,
    approximate_busy_until timestamp(0) default NULL::timestamp without time zone,
    last_busy_at           timestamp(0) default NULL::timestamp without time zone
);

create type courier_shift_event_type as enum ('started', 'paused', 'unpaused', 'stopped');
create type courier_shift_event_source as enum ('supervisor', 'courier', 'system');

create table courier_shift_events
(
    id            bigserial                  not null
        constraint courier_shift_events_pkey
            primary key,
    shift_id      bigint                     not null,
    event_type    courier_shift_event_type   not null,
    event_source  courier_shift_event_source not null,
    latitude      numeric(10, 6),
    longitude     numeric(10, 6),
    created_at    timestamp(0)               not null,
    courier_id    integer                    not null,
    registered_at timestamp(0)               not null
);

COMMIT;
