drop schema if exists audit_events cascade;
create schema audit_events;

create table audit_events.actions (
    id serial primary key,
    action text not null unique
);

create table audit_events.systems (
    id serial primary key,
    name text not null unique
);

create table audit_events.logs (
    id text primary key,  -- сюда пишется uuid, с монги строковый ObjectId
    action_id int not null references audit_events.actions (id),
    login text not null,
    object_id text,
    ticket text,
    timestamp timestamp not null,
    request_id text,
    arguments json not null,
    arguments_id text,
    system_id int not null references audit_events.systems (id)
);

create index audit_events_logs_action_id_object_id on audit_events.logs (action_id, object_id);
create index audit_events_logs_timestamp_action_id on audit_events.logs (timestamp, action_id);
create index audit_events_logs_ticket on audit_events.logs (ticket);
create unique index audit_events_logs_request_id on audit_events.logs (request_id);
create index audit_events_logs_login on audit_events.logs (login);
create index audit_events_logs_system_id on audit_events.logs (system_id);
create index audit_events_logs_arguments_id on audit_events.logs (arguments_id);

create function audit_events.set_logs_arguments_id() returns trigger as $$
begin
    new.arguments_id := json_extract_path_text(new.arguments, '_id');
    return new;
end;
$$ language plpgsql;

create trigger set_arguments_id before insert on audit_events.logs for each row
    execute procedure audit_events.set_logs_arguments_id();
