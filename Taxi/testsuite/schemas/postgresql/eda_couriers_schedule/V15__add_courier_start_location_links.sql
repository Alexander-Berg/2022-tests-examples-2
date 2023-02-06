START TRANSACTION;

create table courier_start_location_links
(
    id                bigserial
        primary key,
    created_at        timestamp(0) with time zone default now() not null,
    updated_at        timestamp(0) with time zone default now() not null,
    courier_id        bigint                                    not null,
    start_location_id bigint                                    not null
);

comment on column courier_start_location_links.id is '(DC2Type:int64)';

comment on column courier_start_location_links.courier_id is 'Id курьера(DC2Type:int64)';

comment on column courier_start_location_links.start_location_id is 'Id привязанной точки старта(DC2Type:int64)';

create index idx__courier_start_location_links__courier_id
    on courier_start_location_links (courier_id);

create index idx__courier_start_location_links__start_location_id
    on courier_start_location_links (start_location_id);

create index idx__courier_start_location_links__created_at
    on courier_start_location_links (created_at);

create index idx__courier_start_location_links__updated_at
    on courier_start_location_links (updated_at);

create unique index ux__courier_start_location_links__courier_id__start_location_id
    on courier_start_location_links (courier_id, start_location_id);


COMMIT;
