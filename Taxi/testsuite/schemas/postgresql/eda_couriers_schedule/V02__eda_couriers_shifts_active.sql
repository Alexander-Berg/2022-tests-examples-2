START TRANSACTION;

create sequence public.courier_active_shifts__update_seq_id;

create type public.courier_active_shift_state as enum ('in_progress', 'paused', 'closed');

create type public.courier_active_shift_consumer as enum ('candidates', 'picker-dispatch');

create table public.courier_active_shifts
(
    id            bigserial
        constraint courier_active_shifts_pkey
            primary key,
    courier_id    integer                                                                                       not null,
    shift_id      bigint                                                                                        not null,
    state         courier_active_shift_state                                                                    not null,
    high_priority boolean                                                                                       not null,
    zone_id       integer                                                                                       not null,
    metagroup_id  varchar(128)                default NULL::character varying,
    zone_group_id integer,
    unpauses_at   timestamp(0) with time zone default NULL::timestamp without time zone,
    closes_at     timestamp(0) with time zone                                                                   not null,
    started_at    timestamp(0) with time zone                                                                   not null,
    created_at    timestamp(0) with time zone                                                                   not null,
    updated_at    timestamp(0) with time zone default CURRENT_TIMESTAMP                                         not null,
    paused_at     timestamp(0) with time zone default NULL::timestamp without time zone,
    update_seq_id bigint                      default nextval('courier_active_shifts__update_seq_id'::regclass) not null,
    consumer      courier_active_shift_consumer default 'candidates'::courier_active_shift_consumer             not null
);

comment on column courier_active_shifts.id is '(DC2Type:int64)';

comment on column courier_active_shifts.courier_id is 'Id курьера';

comment on column courier_active_shifts.shift_id is 'Id смены(DC2Type:int64)';

comment on column courier_active_shifts.state is 'Состояние смены (in_progress, paused, closed)(DC2Type:courier_active_shift_state)';

comment on column courier_active_shifts.high_priority is 'Приоритетность';

comment on column courier_active_shifts.zone_id is 'Id зоны';

comment on column courier_active_shifts.metagroup_id is 'Id метагруппы';

comment on column courier_active_shifts.zone_group_id is 'Id логистической группы';

comment on column courier_active_shifts.unpauses_at is 'Плановое время выхода с паузы';

comment on column courier_active_shifts.closes_at is 'Время закрытия смены';

comment on column courier_active_shifts.started_at is 'Время старта смены';

comment on column courier_active_shifts.paused_at is 'Время ухода на паузу';

comment on column courier_active_shifts.update_seq_id is 'Id в порядке изменения строк(DC2Type:int64)';

create index idx__courier_active_shifts__created_at
    on courier_active_shifts (created_at);

create index idx__courier_active_shifts__updated_at
    on courier_active_shifts (updated_at);

create unique index uq__courier_active_shifts__courier_id
    on courier_active_shifts (courier_id);

create unique index uq__courier_active_shifts__shift_id
    on courier_active_shifts (shift_id);

create index idx__courier_active_shifts__updated_at__id
    on courier_active_shifts (updated_at, id);

create index idx__courier_active_shifts__update_seq_id
    on courier_active_shifts (update_seq_id);


COMMIT;
