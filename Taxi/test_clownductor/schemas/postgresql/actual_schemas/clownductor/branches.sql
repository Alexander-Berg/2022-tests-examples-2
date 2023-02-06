create table clownductor.branches (
    -- just an id
    id serial unique primary key,
    -- part of what service this branch is
    service_id integer references
        clownductor.services (id) on delete cascade,
    -- name of the branch
    name text not null,
        -- environment type
    env environment_type not null default 'unstable',
    -- direct link to the cluster (at condector, nanny, pgaas, etc.)
    direct_link text default null,
    -- version of the artifact currently deployed to this branch
    artifact_version text default null,
    configs jsonb not null default '[]'::jsonb,
    deleted_at integer default null,
    balancer_id integer references clownductor.branches (id),
    endpointsets jsonb not null default '[]'::jsonb,
    updated_at integer not null default extract(epoch from now())
);

create unique index branches_service_id_name_key_deleted_at_unique
    on clownductor.branches
        (service_id, name)
where
    deleted_at is null
;

CREATE INDEX clownductor_branches_direct_link
    ON clownductor.branches (direct_link);

create function clownductor.set_branch_updated_at() returns trigger as $$
begin
    new.updated_at := extract(epoch from now());
    return new;
end;
$$ language plpgsql;

create trigger set_branch_updated_at_tr
before insert or update on clownductor.branches
for each row
execute procedure clownductor.set_branch_updated_at();
