START TRANSACTION;

create table courier_shift_total_durations
(
    id         bigserial
        primary key,
    courier_id integer                not null,
    start_at   timestamp(0)           not null,
    finish_at  timestamp(0)           not null,
    total_time integer      default 0 not null,
    created_at timestamp(0)           not null,
    updated_at timestamp(0) default NULL::timestamp without time zone
);

comment on column courier_shift_total_durations.courier_id is 'ID курьера';

comment on column courier_shift_total_durations.start_at is 'Начало периода';

comment on column courier_shift_total_durations.finish_at is 'Конец периода';

comment on column courier_shift_total_durations.total_time is 'Выбранная продолжительность рабочего времени';

create unique index ux__courier_shift_total_durations__start_at__finish_at__courier
    on courier_shift_total_durations (start_at, finish_at, courier_id);

COMMIT;
