START TRANSACTION;
create table start_locations
(
    id                 bigserial
        primary key,
    region_id          integer                    not null,
    name               varchar(255)               not null,
    latitude           double precision           not null,
    longitude          double precision           not null,
    deleted_at         timestamp(0) default NULL::timestamp without time zone,
    created_at         timestamp(0) default now() not null,
    updated_at         timestamp(0) default now() not null,
    logistics_group_id bigint
);

comment on column start_locations.id is '(DC2Type:int64)';

comment on column start_locations.region_id is 'ID региона';

comment on column start_locations.name is 'Название';

comment on column start_locations.latitude is 'Широта';

comment on column start_locations.longitude is 'Долгота';

comment on column start_locations.deleted_at is 'Время удаления';

comment on column start_locations.logistics_group_id is 'Id логистической группы(DC2Type:int64)';

create index idx__start_locations__region_id
    on start_locations (region_id);

create index idx__start_locations__created_at
    on start_locations (created_at);

create index idx__start_locations__updated_at
    on start_locations (updated_at);

create index idx__start_locations__logistics_group_id
    on start_locations (logistics_group_id);

COMMIT;
