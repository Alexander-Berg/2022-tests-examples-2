START TRANSACTION;

create table courier_start_location_availability_flags
(
    id         bigserial
        primary key,
    courier_id integer                    not null,
    flag_name  varchar(64)                not null,
    deleted_at timestamp(0) default NULL::timestamp without time zone,
    created_at timestamp(0) default now() not null,
    updated_at timestamp(0) default now() not null
);

comment on column courier_start_location_availability_flags.id is '(DC2Type:int64)';

comment on column courier_start_location_availability_flags.courier_id is 'ID курьера';

comment on column courier_start_location_availability_flags.flag_name is 'Код флага доступности';

comment on column courier_start_location_availability_flags.deleted_at is 'Время удаления';

create index idx__courier_start_location_availability_flags__courier_id
    on courier_start_location_availability_flags (courier_id);

create index idx__courier_start_location_availability_flags__created_at
    on courier_start_location_availability_flags (created_at);

create index idx__courier_start_location_availability_flags__updated_at
    on courier_start_location_availability_flags (updated_at);

create unique index ux__courier_start_location_availability_flags__courier_id__flag
    on courier_start_location_availability_flags (courier_id, flag_name);

COMMIT;
