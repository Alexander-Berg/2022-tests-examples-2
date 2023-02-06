create type perforator.services_warranty_action as enum (
    'create',
    'edit',
    'delete'
);

create table perforator.services_warranty (
    id bigserial primary key,
    tvm_name text not null,
    env_type perforator.env_type not null,
    tvm_id bigint,
    action perforator.services_warranty_action not null,
    ensured boolean not null default false,
    attempts int not null default 0,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
);

create unique index services_warranty_tvm_name_env_type_ensured_false_unique
    on perforator.services_warranty (tvm_name, env_type, ensured)
    where ensured is false;

create type perforator.rules_warranty_action as enum (
    'create',
    'delete'
);

create table perforator.rules_warranty (
    id bigserial primary key,
    source text not null,
    destination text not null,
    env_type perforator.env_type not null,
    action perforator.rules_warranty_action not null,
    ensured boolean not null default false,
    attempts int not null default 0,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
);

create unique index
    rules_warranty_source_destination_env_type_ensured_false_unique
        on perforator.rules_warranty (source, destination, env_type, ensured)
        where ensured is false;


create trigger services_warranty_set_updated
    before update or insert on perforator.services_warranty
    for each row execute procedure perforator.set_updated();

create trigger rules_warranty_set_updated
    before update or insert on perforator.rules_warranty
    for each row execute procedure perforator.set_updated();
