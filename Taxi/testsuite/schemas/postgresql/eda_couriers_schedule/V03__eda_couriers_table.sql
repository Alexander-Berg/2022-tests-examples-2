START TRANSACTION;
create type public.courier_type as enum ('pedestrian', 'bicycle', 'vehicle');
create type public.courier_work_status as enum ('active', 'blocked', 'on_vacation', 'ill', 'deactivated', 'lost', 'inactive', 'candidate');
create type public.courier_service as enum ('eats', 'driver-profiles');

create table courier_groups
(
    id         serial
        primary key,
    name       varchar(32)                            not null,
    created_at timestamp(0) default CURRENT_TIMESTAMP not null,
    updated_at timestamp(0) default CURRENT_TIMESTAMP not null
);

comment on table courier_groups is 'Группы курьеров';

comment on column courier_groups.name is 'Название';

create index idx__courier_groups__created_at
    on courier_groups (created_at);

create index idx__courier_groups__updated_at
    on courier_groups (updated_at);


create table couriers
(
    id                                       integer                                not null
        primary key,
    group_id                                 integer
        constraint fk__couriers__group_id
            references courier_groups,
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
    is_fixed_shifts_option_enabled           boolean      default false             not null,
    subpool                                 varchar(255) default NULL::character varying
);

comment on table couriers is 'Курьеры';

comment on column couriers.region_id is 'ID региона';

comment on column couriers.courier_type is 'Тип курьера(DC2Type:courier_type)';

comment on column couriers.name is 'Имя пользователя';

comment on column couriers.work_status is 'Статус курьера(DC2Type:courier_work_status)';

comment on column couriers.service is 'Система курьера(DC2Type:courier_service)';

comment on column couriers.external_id is 'Внешний id курьера';

comment on column couriers.pool_name is 'Пул курьера';

comment on column couriers.logistics_group_id is 'Id логистической группы';

comment on column couriers.birthday is 'Дата рождения';

comment on column couriers.is_storekeeper is 'Является ли кладовщиком';

comment on column couriers.is_dedicated_picker is 'Является ли выделенным сборщиком';

comment on column couriers.is_picker is 'Является ли мастером покупок';

comment on column couriers.use_logistics_group_for_unplanned_shifts is 'Учитывать ли логистическую группу курьера на свободных слотах';

comment on column couriers.is_park_courier is 'Курьер, привлеченный из парка';

comment on column couriers.is_rover is 'Ровер';

comment on column couriers.is_fixed_shifts_option_enabled is 'Опция Фиксированные слоты';

create index fk__couriers__group_id
    on couriers (group_id);

create unique index uq__couriers__external_id
    on couriers (external_id);

create index idx__couriers__created_at
    on couriers (created_at);

create index idx__couriers__updated_at
    on couriers (updated_at);


COMMIT;
