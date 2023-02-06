START TRANSACTION;

create table courier_shifts_counters
(
    performer_id varchar(255)                                          not null
        primary key,
    total_shifts integer                     default 0                 not null,
    created_at   timestamp(0) with time zone default CURRENT_TIMESTAMP not null,
    updated_at   timestamp(0) with time zone default CURRENT_TIMESTAMP not null
);

create index idx__courier_shifts_counters__performer_id
    on courier_shifts_counters (performer_id);


COMMIT;
