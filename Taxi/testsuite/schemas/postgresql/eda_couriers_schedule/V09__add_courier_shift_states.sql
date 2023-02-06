START TRANSACTION;

create table courier_shift_states
(
    id             bigserial
        primary key,
    shift_id       bigint                                 not null,
    started_at     timestamp(0)                           not null,
    finished_at    timestamp(0) default NULL::timestamp without time zone,
    duration       integer,
    updated_at     timestamp(0) default CURRENT_TIMESTAMP not null,
    pause_duration integer,
    created_at     timestamp(0) default CURRENT_TIMESTAMP not null
);

comment on table courier_shift_states is 'Состояние смен';

comment on column courier_shift_states.shift_id is 'ID смены(DC2Type:int64)';

comment on column courier_shift_states.started_at is 'Время фактического начала смены';

comment on column courier_shift_states.finished_at is 'Время фактического окончания смены';

comment on column courier_shift_states.duration is 'Продолжительность смены в секундах';

comment on column courier_shift_states.pause_duration is 'Продолжительность паузы на смене';

create index idx__courier_shift_states__finished_at
    on courier_shift_states (finished_at);

create index idx__courier_shift_states__started_at
    on courier_shift_states (started_at);

create index idx__courier_shift_states__updated_at
    on courier_shift_states (updated_at);

create unique index uq__courier_shift_state__shift_id
    on courier_shift_states (shift_id);

create index idx__courier_shift_states__created_at
    on courier_shift_states (created_at);

COMMIT;
