create table clownductor.services (
    -- just an id
    id serial unique primary key,
    -- part of what project this service is
    project_id integer references
        clownductor.projects (id) on delete cascade,
    -- name of the service
    name text not null,
    -- if this service started to receive production traffic
    production_ready boolean default false,
    -- what we want to deploy here (usually docker image name)
    artifact_name text not null,
    -- what type of cluster we have here (nanny, conductor, postgres, etc.)
    cluster_type cluster_type not null,
    -- path to the wiki page with service description
    wiki_path text default null,
    -- abc-service associated with this service
    abc_service text default null,
    -- abc-service with test tvm
    tvm_testing_abc_service text default null,
    -- abc-service with stable tvm
    tvm_stable_abc_service text default null,
    -- startrek task where this service was developed
    direct_link text default null,
    new_service_ticket text default null,
    requester text default null,
    design_review_ticket text default null,
    service_url text default null,
    deleted_at integer default null,
    idempotency_token text default null,
    created_at integer not null default extract(epoch from now())::integer
);

create unique index services_project_id_service_name_type_deleted_at_unique
    on clownductor.services
        (project_id, name, cluster_type)
where
    deleted_at is null
;

create index clownductor_services_project_id_cluster_type
    on clownductor.services (project_id, cluster_type);

create unique index clownductor_services_idempotency_token_unique
    ON clownductor.services (idempotency_token);

CREATE INDEX clownductor_service_created_at
    ON clownductor.services (created_at);
