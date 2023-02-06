create table clownductor.projects (
    -- just an id
    id serial unique primary key,
    -- name of the project
    name text not null,
    -- network for all non-production branches
    network_testing text not null,
    -- network for all production branches
    network_stable text not null,
    -- abc-service slug associated with all services inside the project
    service_abc text not null,
    -- abc-service slug containing yp quota for all services inside the project
    yp_quota_abc text not null,
    -- abc-service slug with all tvm subservices
    tvm_root_abc text not null,
    owners jsonb not null default '{}'::jsonb,
    approving_managers jsonb not null default '{}'::jsonb,
    approving_devs jsonb not null default '{}'::jsonb,
    env_params jsonb not null default '{}'::jsonb,
    pgaas_root_abc text,
    responsible_team jsonb not null default '{}'::jsonb,
    yt_topic jsonb not null default '{}'::jsonb,
    deleted_at integer default null,
    namespace_id integer not null references clownductor.namespaces (id),
    unique (name)
);

create index clownductor_projects_namespace_id
    on clownductor.projects (namespace_id);
