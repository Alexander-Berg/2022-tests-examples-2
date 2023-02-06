START TRANSACTION;

create table public.performer_quality_controls
(
    id              bigserial
        constraint performer_quality_controls_pkey
            primary key,
    performer_id    varchar(255)                              not null,
    control_type    varchar(255)                              not null,
    next_control_at timestamp(0) with time zone default NULL::timestamp with time zone,
    created_at      timestamp(0) with time zone default now() not null,
    updated_at      timestamp(0) with time zone default now() not null
);

comment on column performer_quality_controls.performer_id is 'ID исполнителя';

comment on column performer_quality_controls.control_type is 'Тип контроля';

comment on column performer_quality_controls.next_control_at is 'Время следующего контроля';

create index idx__performer_quality_controls__created_at
    on performer_quality_controls (created_at);

create index idx__performer_quality_controls__updated_at
    on performer_quality_controls (updated_at);

create unique index ux__performer_quality_controls__performer_id__control_type__nex
    on performer_quality_controls (performer_id, control_type);

COMMIT;
