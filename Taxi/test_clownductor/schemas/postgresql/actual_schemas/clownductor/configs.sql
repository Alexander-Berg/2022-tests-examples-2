create table clownductor.configs (
    id  bigserial primary key,
    branch_id integer references clownductor.branches(id) on delete cascade,
    name text not null,
    plugins text[],
    libraries text[],
    is_service_yaml boolean,
    updated_at integer not null default extract (epoch from now())
);

create index configs_branch_id on clownductor.configs (branch_id);
create unique index configs_name_branch_id on clownductor.configs (name, branch_id);
create index configs_plugins on clownductor.configs using GIN (plugins array_ops);
create index configs_libraries on clownductor.configs using GIN (libraries array_ops);
create index configs_in_service_yaml on clownductor.configs (is_service_yaml);

create function clownductor.configs_update_at() returns trigger as $$
begin
    new.updated_at := extract (epoch from now());
    return new;
end;
$$ language plpgsql;

create trigger set_update_at_tr
    before insert or update
    on clownductor.configs
    for each row
execute procedure clownductor.configs_update_at();
