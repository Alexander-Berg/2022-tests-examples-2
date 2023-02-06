START TRANSACTION;

create table timetable_weekday_settings
(
    id                            serial
        primary key,
    timetable_setting_id          integer                                not null
        constraint fk_1d6173c4f77e3e7e
            references timetable_settings,
    weekday                       smallint                               not null,
    is_enabled                    boolean                                not null,
    are_additional_shifts_allowed boolean                                not null,
    created_at                    timestamp(0) default CURRENT_TIMESTAMP not null,
    updated_at                    timestamp(0) default CURRENT_TIMESTAMP not null,
    permissions                   json
);

comment on table timetable_weekday_settings is 'Настройки графика по дням недели';

comment on column timetable_weekday_settings.weekday is 'День недели, к которому относится запись. 0 - понедельник, 6 - воскресенье';

comment on column timetable_weekday_settings.is_enabled is 'Включен ли выбор смен в этот день';

comment on column timetable_weekday_settings.are_additional_shifts_allowed is 'Доступен ли выбор дополнительных и перевыставленных смен (не плановых)';

comment on column timetable_weekday_settings.permissions is 'Настройки доступа курьерских групп к выбору смен(DC2Type:timetable_permissions)';

create index fk__timetable_weekday_settings__timetable_setting_id
    on timetable_weekday_settings (timetable_setting_id);

create unique index uq__timetable_weekday_settings__timetable_setting_id__weekday
    on timetable_weekday_settings (timetable_setting_id, weekday);

create index idx__timetable_weekday_settings__created_at
    on timetable_weekday_settings (created_at);

create index idx__timetable_weekday_settings__updated_at
    on timetable_weekday_settings (updated_at);

COMMIT;
