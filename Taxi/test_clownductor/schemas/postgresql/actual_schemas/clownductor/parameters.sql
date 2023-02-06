create table clownductor.parameters (
    id bigserial primary key,
    subsystem_name text not null,
    service_id integer references clownductor.services(id) on delete cascade,
    branch_id integer references clownductor.branches(id) on delete cascade,
    service_values jsonb,
    remote_values jsonb,
    updated_at integer not null
);

create index parameters_service_id on clownductor.parameters (service_id);
create index parameters_branch_id on clownductor.parameters (branch_id);
create unique index parameters_subsystem_name_service_id_branch_id_unique
 on clownductor.parameters (subsystem_name, service_id, branch_id);

create function clownductor.parameters_update_at() returns trigger as $$
begin
    new.updated_at := extract (epoch from now());
    return new;
end;
$$ language plpgsql;

create trigger set_update_at_tr
before insert or update on clownductor.parameters
for each row
execute procedure clownductor.parameters_update_at();
