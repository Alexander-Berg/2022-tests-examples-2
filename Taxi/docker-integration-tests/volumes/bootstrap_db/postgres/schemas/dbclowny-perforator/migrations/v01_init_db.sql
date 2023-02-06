create schema perforator;

create function perforator.set_updated() returns trigger as $set_updated$
    begin
        new.updated_at = now();
        return new;
    end;
$set_updated$ language plpgsql;

create type perforator.env_type as enum (
    'unstable',
    'testing',
    'production'
);

create table perforator.services (
    id bigserial primary key,
    clown_id bigint unique,
    tvm_name text not null unique,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
);


create table perforator.environments (
    id bigserial primary key,
    service_id bigint not null
        references perforator.services (id) on delete cascade,
    env_type perforator.env_type not null,
    tvm_id bigint not null,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now(),

    unique (service_id, env_type)
);

create table perforator.environment_rules (
    id bigserial primary key,
    source_env_id bigint not null
        references perforator.environments (id) on delete restrict,
    destination_env_id bigint not null
        references perforator.environments (id) on delete restrict,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now(),

    unique (source_env_id, destination_env_id)
);

create trigger services_set_updated
    before update or insert on perforator.services
    for each row execute procedure perforator.set_updated();

create trigger environments_set_updated
    before update or insert on perforator.environments
    for each row execute procedure perforator.set_updated();

create trigger environment_rules_set_updated
    before update or insert on perforator.environment_rules
    for each row execute procedure perforator.set_updated();
