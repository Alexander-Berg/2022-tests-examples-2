START TRANSACTION;

create table region_settings
(
    id         bigserial
        primary key,
    region_id  integer                    not null,
    name       varchar(64)                not null,
    value      text,
    type       varchar(64)                not null,
    updated_at timestamp(0) default now() not null,
    created_at timestamp(0) default now() not null
);

comment on table region_settings is 'Региональные настройки';

comment on column region_settings.region_id is 'ID региона';

comment on column region_settings.name is 'Название настройки';

comment on column region_settings.value is 'Значение настройки';

comment on column region_settings.type is 'Тип настройки: string, unsigned_int, bool, time, interval(DC2Type:region_setting_type)';

create unique index ux__region_settings__region_id_name
    on region_settings (region_id, name);

COMMIT;
