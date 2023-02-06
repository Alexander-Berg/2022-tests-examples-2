START TRANSACTION;

create type public.courier_shift_event_type as enum ('started', 'paused', 'unpaused', 'stopped');
create type public.courier_shift_event_source as enum ('supervisor', 'courier', 'system');

create table courier_shift_events
(
    id            bigserial
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

comment on table courier_shift_events is 'События на сменах';

comment on column courier_shift_events.shift_id is 'ID смены(DC2Type:int64)';

comment on column courier_shift_events.event_type is 'Тип события';

comment on column courier_shift_events.event_source is 'Источник события';

comment on column courier_shift_events.latitude is 'Координаты курьера в момент события: широта';

comment on column courier_shift_events.longitude is 'Координаты курьера в момент события: долгота';

comment on column courier_shift_events.courier_id is 'ID курьера';

comment on column courier_shift_events.registered_at is 'Дата регистрации события';

create index idx__courier_shift_event__courier_id
    on courier_shift_events (courier_id);

create index idx__courier_shift_event__shift_id
    on courier_shift_events (shift_id);

create index idx__courier_shift_events__created_at
    on courier_shift_events (created_at);


COMMIT;
