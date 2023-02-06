create table clownductor.variables (
    id bigserial primary key,
    subsystem_name text not null,
    service_id integer references clownductor.services(id),
    branch_id integer references clownductor.branches(id),
    service_values jsonb,
    remote_values jsonb,
    updated_at integer not null
);

create index variables_service_id on clownductor.variables (service_id);
create index variables_branch_id on clownductor.variables (branch_id);
create unique index variables_subsystem_name_service_id_branch_id
 on clownductor.variables (subsystem_name, service_id, branch_id);

create function clownductor.variables_update_at() returns trigger as $$
begin
    new.updated_at := extract (epoch from now());
    return new;
end;
$$ language plpgsql;

create trigger set_update_at_tr
before insert or update on clownductor.variables
for each row
execute procedure clownductor.variables_update_at();
