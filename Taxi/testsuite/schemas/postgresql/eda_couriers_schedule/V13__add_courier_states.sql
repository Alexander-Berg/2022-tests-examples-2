START TRANSACTION;

create type public.courier_state_type as enum ('online', 'offline', 'logged out');

create table courier_states
(
    courier_id             integer                    not null
        primary key,
    state                  courier_state_type         not null,
    updated_at             timestamp(0)               not null,
    last_online            timestamp(0) default NULL::timestamp without time zone,
    is_busy                boolean      default false not null,
    approximate_busy_until timestamp(0) default NULL::timestamp without time zone,
    last_busy_at           timestamp(0) default NULL::timestamp without time zone
);

comment on table courier_states is 'Состояние курьеров, информация о наличии их онлайн';

comment on column courier_states.courier_id is 'ID курьера';

comment on column courier_states.state is 'Состояние курьера (online, offline, logged out)(DC2Type:courier_state_type)';

comment on column courier_states.last_online is 'Время последнего онлайна';

comment on column courier_states.is_busy is 'Признак занятости курьера';

comment on column courier_states.approximate_busy_until is 'Предположительно занят до';

comment on column courier_states.last_busy_at is 'Время последней занятости';

create index idx__courier_states__last_online
    on courier_states (last_online);

COMMIT;
