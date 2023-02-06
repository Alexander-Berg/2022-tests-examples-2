START TRANSACTION;

create table timetable_settings
(
    id                  serial
        primary key,
    region_id           integer                                not null,
    updated_at          timestamp(0) default CURRENT_TIMESTAMP not null,
    shifts_min_interval integer                                not null,
    created_at          timestamp(0) default CURRENT_TIMESTAMP not null
);

comment on table timetable_settings is 'Настройки графика в регионе';

comment on column timetable_settings.region_id is 'ID региона';

comment on column timetable_settings.shifts_min_interval is 'Минимальное время между сменами для выбора на разных локациях';

create unique index uq__timetable_settings__region_id
    on timetable_settings (region_id);

create index idx__timetable_settings__created_at
    on timetable_settings (created_at);

create index idx__timetable_settings__updated_at
    on timetable_settings (updated_at);

COMMIT;
