START TRANSACTION;

create type public.shift_pool as enum ('courier', 'storekeeper', 'dedicated_picker', 'picker', 'park_courier', 'relocator', 'shift_master');
create type public.shift_service as enum ('eda', 'lavka', 'shop', 'scooter');
create type public.shift_status as enum ('planned', 'in_progress', 'on_pause', 'closed', 'not_started', 'draft', 'deleted', 'scheduled_pause');
create type public.shift_type as enum ('planned', 'planned-extra', 'replacement', 'unplanned', 'fixed');

create sequence analytics_timetable_seq;


create table public.courier_shifts
(
    id                           bigint         default nextval('analytics_timetable_seq'::regclass) not null
        constraint courier_shifts_pkey
            primary key,
    courier_offline_time          integer                                                             not null,
    courier_id                   integer,
    updated_at                   timestamp(0)   default CURRENT_TIMESTAMP                            not null,
    status                       shift_status   default 'planned'::public.shift_status               not null,
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
    service                      shift_service,
    additional_payment_per_order numeric(13, 2)
);

comment on table courier_shifts is 'Смены';

comment on column courier_shifts.courier_offline_time is 'Офлайн время курьера на смене';

comment on column courier_shifts.courier_id is 'ID курьера';

comment on column courier_shifts.status is 'Статус смены(DC2Type:shift_status)';

comment on column courier_shifts.has_lateness is 'Признак опоздания';

comment on column courier_shifts.has_early_leaving is 'Признак раннего ухода';

comment on column courier_shifts.is_abandoned is 'Признак того, что курьер покинул смену';

comment on column courier_shifts.region_id is 'ID города';

comment on column courier_shifts.zone_id is 'ID зоны';

comment on column courier_shifts.start_time is 'Начало смены';

comment on column courier_shifts.end_time is 'Окончание смены';

comment on column courier_shifts.date is 'дата смены';

comment on column courier_shifts.courier_type is '(DC2Type:legacy_courier_type)';

comment on column courier_shifts.parent_id is 'id смены, вместо которой была выставлена эта. null - предка нет';

comment on column courier_shifts.courier_assigned_at is 'Время последнего назначения курьера на смену';

comment on column courier_shifts.mass_upload_id is 'Id для связи с записью массовой заливки слотов';

comment on column courier_shifts.type is 'Тип слота (planned, planned-extra, replacement, unplanned)(DC2Type:shift_type)';

comment on column courier_shifts.external_id is 'Id во внешней системе, указанный при создании смены';

comment on column courier_shifts.is_zone_checked is 'Признак того, что зона при старте была проверена';

comment on column courier_shifts.guarantee is 'Размер гарантии';

comment on column courier_shifts.pool is 'Пул смены(DC2Type:shift_pool)';

comment on column courier_shifts.logistics_group_id is 'Id логистической группы слота';

comment on column courier_shifts.effective_logistics_group_id is 'Id рассчитанной логистической группы слота';

comment on column courier_shifts.start_location_id is 'ID точки старта(DC2Type:int64)';

comment on column courier_shifts.service is 'Сервис, к которому относится смена(DC2Type:shift_service)';

create index idx__courier_shifts__courier_id
    on courier_shifts (courier_id);

create index idx__courier_shifts__created_at
    on courier_shifts (created_at);

create index idx__courier_shifts__updated_at
    on courier_shifts (updated_at);

create index idx__courier_shifts__external_id
    on courier_shifts (external_id);

create index idx__courier_shifts__is_zone_checked__created_at
    on courier_shifts (is_zone_checked, created_at);

create index idx__courier_shifts__zone_id
    on courier_shifts (zone_id);

create index idx__courier_shifts__courier_id__date
    on courier_shifts (courier_id, date);

create index idx__courier_shifts__date__zone_id__courier_id
    on courier_shifts (date, zone_id, courier_id);

create index idx__courier_shifts__zone_id__start_time__end_time
    on courier_shifts (zone_id, start_time, end_time);

create index idx__courier_shifts__start_time__end_time
    on courier_shifts (start_time, end_time);

create index idx__courier_shifts__date__status__courier_type
    on courier_shifts (date, status, courier_type);


create table public.point_start_list
(
    point_start_id     integer                                not null
        constraint point_start_list_pkey
            primary key,
    city_id            integer                                not null,
    point_start_name   varchar(255)                           not null,
    point_start_status integer      default 1                 not null,
    zone_ff_time_add   integer      default 0                 not null,
    metagroup_id       varchar(128) default NULL::character varying,
    group_id           integer,
    created_at         timestamp(0) default CURRENT_TIMESTAMP not null,
    updated_at         timestamp(0) default CURRENT_TIMESTAMP not null
);

comment on column point_start_list.point_start_id is 'ID зон работы FF';

comment on column point_start_list.city_id is 'ID города/ ID совпадает с ID в базе FF';

comment on column point_start_list.point_start_name is 'Название зоны FF';

comment on column point_start_list.point_start_status is '0 - не работает; 1 - работает(DC2Type:courier_delivery_zone_status)';

comment on column point_start_list.zone_ff_time_add is 'Хранит время добавления данных на сайт';

comment on column point_start_list.metagroup_id is 'Id метагруппы';

comment on column point_start_list.group_id is 'Id логистической группы';

create index idx__point_start_list__city_id
    on point_start_list (city_id);

create index idx__point_start_list__metagroup_id
    on point_start_list (metagroup_id);

create index idx__point_start_list__point_start_name
    on point_start_list (point_start_name);

create index idx__point_start_list__created_at
    on point_start_list (created_at);

create index idx__point_start_list__updated_at
    on point_start_list (updated_at);


create table public.courier_shift_change_requests
(
    shift_id    bigint                                 not null
        constraint courier_shift_change_requests_pkey
            primary key,
    changeset   json,
    is_approved boolean,
    updated_at  timestamp(0) default CURRENT_TIMESTAMP not null,
    created_at  timestamp(0) default CURRENT_TIMESTAMP not null
);

comment on column courier_shift_change_requests.shift_id is 'ID смены';

comment on column courier_shift_change_requests.changeset is 'Список изменений по смене (json)';

comment on column courier_shift_change_requests.is_approved is 'Признак принял ли курьер изменения';

create index idx__courier_shift_change_requests__is_approved
    on courier_shift_change_requests (is_approved);

create index idx__courier_shift_change_requests__created_at
    on courier_shift_change_requests (created_at);

create index idx__courier_shift_change_requests__updated_at
    on courier_shift_change_requests (updated_at);


create table public.regions
(
    id                  integer                                not null
        constraint regions_pkey
            primary key,
    name                varchar(100)                           not null,
    time_zone_vs_moscow integer                                not null,
    is_available        boolean      default true              not null,
    country_code        char(2)                                not null,
    created_at          timestamp(0) default CURRENT_TIMESTAMP not null,
    updated_at          timestamp(0) default CURRENT_TIMESTAMP not null
);

comment on column regions.name is 'Имя города';

comment on column regions.time_zone_vs_moscow is 'Разница по времени с Москвой в часах';

comment on column regions.is_available is 'Признак доступности региона';

comment on column regions.country_code is 'Код страны ISO 3166-1 alpha-2';

create unique index uq__regions__name
    on regions (name)
    where (is_available = true);

create index idx__regions__created_at
    on regions (created_at);

create index idx__regions__updated_at
    on regions (updated_at);

COMMIT;
