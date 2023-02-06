create table audit_events.tmp_lost_logs (
    id serial primary key,
    timestamp timestamp not null,
    mongo_id text not null,
    ignore_logs json
);
