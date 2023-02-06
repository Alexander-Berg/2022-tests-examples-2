drop schema if exists task_processor cascade;
create schema task_processor;

create type JOB_STATUS as enum (
    'inited',
    'in_progress',
    'success',
    'failed',
    'canceled'
);

-- provider info aka consumer
create table task_processor.providers (
    id serial unique primary key,
    name text not null unique,
    tvm_id integer not null,
    created_at integer not null default extract (epoch from now()),
    updated_at integer not null,
    hostname text not null,
    tvm_name text not null
);

create table task_processor.recipes (
    id serial unique primary key,
    name text not null,
    provider_id integer not null references task_processor.providers (id),
    created_at integer not null default extract (epoch from now()),
    updated_at integer not null default extract (epoch from now()),
    job_vars jsonb not null default '[]'::jsonb, -- list required fields in job_variables for create_job
    version integer not null default 1, -- list required fields in job_variables for create_job

    unique (provider_id, name, version)
);

create index task_processor_recipes_name on task_processor.recipes (name);

create table task_processor.cubes (
    id serial unique primary key,
    name text not null,
    provider_id integer not null references task_processor.providers (id),
    created_at integer default extract (epoch from now()),
    updated_at integer not null,
    needed_parameters jsonb default '[]'::jsonb, -- req job_variables fields for input_mapping
    optional_parameters jsonb default  '[]'::jsonb,-- optional job_variables fields for input_mapping
    invalid boolean default false,
    output_parameters jsonb default  '[]'::jsonb,

    unique (provider_id, name)
);

-- relationship recipes & cubes
create table task_processor.stages (
    id serial unique primary key,
    recipe_id integer not null references task_processor.recipes (id) on delete cascade,
    cube_id integer not null references task_processor.cubes (id),
    created_at integer default extract (epoch from now()),
    updated_at integer not null,
    next_id integer references task_processor.stages (id),
    input jsonb default '{}'::jsonb, -- startup input_mapping for init task
    output jsonb default '{}'::jsonb --startup output_mapping for init task
);

create index task_processor_stages_recipe_id
    on task_processor.stages (recipe_id);
create index task_processor_stages_cube_id
    on task_processor.stages (cube_id);
create unique index task_processor_stages_recipe_id_cube_id
 on task_processor.stages (recipe_id, cube_id, next_id);

-- working recipes + history
create table task_processor.jobs (
    id serial unique primary key,
    recipe_id integer references task_processor.recipes (id) on delete cascade,
    name text not null,
    initiator text,
    status JOB_STATUS default 'in_progress'::JOB_STATUS,
    created_at integer default extract (epoch from now()),
    finished_at integer default null,
    error_message text default null,
    idempotency_token text unique,
    change_doc_id text not null,
    real_time integer,
    total_time integer
);

create index task_processor_recipe_id on task_processor.jobs (recipe_id);
create index task_processor_jobs_status on task_processor.jobs (status);
create index task_processor_idempotency_token
    on task_processor.jobs (idempotency_token);

create unique INDEX change_doc_id_key on task_processor.jobs(change_doc_id)
where status = 'in_progress';

-- Variables are updated on almost every step of the job processing.
-- Since each update relocates the row and all indexes should be updated,
-- let's make separate table for this data with only one index.
-- (Also it just seems a bit wrong to me, though currently I don't know how
--  to make right, so making this part separate makes me feel a bit better.)
create table task_processor.job_variables (
    id serial unique primary key,
    job_id integer not null unique references
        task_processor.jobs (id) on delete cascade,
    variables text not null default '{}'
);

-- working cubes
create table task_processor.tasks (
    id serial unique primary key,
    job_id integer not null references
        task_processor.jobs (id) on delete cascade,
    cube_id integer not null references
        task_processor.cubes (id) on delete cascade,
    name text not null,
    input_mapping text,
    output_mapping text,
    payload text default '{}'::text,
    status JOB_STATUS default 'in_progress'::JOB_STATUS,
    error_message text default null,
    sleep_until integer default 0,
    retries integer default 0,
    created_at integer default extract (epoch from now()),
    updated_at integer,
    continue_at integer,
    needed_parameters jsonb default '[]'::jsonb,
    optional_parameters jsonb default  '[]'::jsonb,
    output_parameters jsonb default  '[]'::jsonb,
    started_at integer default null,
    real_time integer,
    total_time integer
);

-- id entity_type
create table task_processor.entity_types (
    id serial unique primary key,
    entity_type text unique not null
);

-- id external_entities_links
create table task_processor.external_entities_links (
    id serial unique primary key,
    external_id text not null,
    entity_type_id integer not null references
        task_processor.entity_types (id) on delete cascade,
    job_id integer not null references
        task_processor.jobs (id) on delete cascade
);

create index external_entities_links_job_id
    on task_processor.external_entities_links(job_id);

create index external_entities_links_external_id_entity_type_id
    on task_processor.external_entities_links(entity_type_id, external_id);

create unique index external_entities_links_entity_type_id_external_id_job_id
    on task_processor.external_entities_links(entity_type_id, external_id, job_id);

create index task_processor_tasks_job_id on task_processor.tasks (job_id);
create index task_processor_tasks_status_sleep_until
    on task_processor.tasks (status, sleep_until);

create table task_processor.task_deps (
    id serial unique primary key,
    prev_task_id integer not null references
        task_processor.tasks (id) on delete cascade,
    next_task_id integer not null references
        task_processor.tasks (id) on delete cascade,

    unique (prev_task_id, next_task_id)
);

create index concurrently task_processor_task_deps_next_task_id
    on task_processor.task_deps (next_task_id);

create table task_processor.locks (
    name text unique primary key,
    job_id integer references task_processor.jobs (id)
);

create function task_processor.trigger_update_at() returns trigger as $$
begin
    new.updated_at := extract (epoch from now());
    return new;
end;
$$ language plpgsql;

create trigger recipes_date_updater before insert or update on task_processor.recipes for each row
execute procedure task_processor.trigger_update_at();
create trigger stages_date_updater before insert or update on task_processor.stages for each row
execute procedure task_processor.trigger_update_at();
create trigger tasks_date_updater before update on task_processor.tasks for each row
execute procedure task_processor.trigger_update_at();
create trigger cubes_date_updater before update on task_processor.cubes for each row
execute procedure task_processor.trigger_update_at();
create trigger providers_date_updater before update on task_processor.providers for each row
execute procedure task_processor.trigger_update_at();

-- Build connection between meta cubes and jobs created by them
-- TAXIPLATFORM-5996
--
create table task_processor.task_job_links (
    id BIGSERIAL primary key,
    -- the job that the task triggers
    child_job_id integer unique
        REFERENCES task_processor.jobs(id),
--     meta task which creates the job
    parent_task_id integer
        REFERENCES task_processor.tasks(id),
    -- the job that the meta task belongs to
    parent_job_id integer
        REFERENCES task_processor.jobs(id)
);

create index task_job_links_child_job_id
    on task_processor.task_job_links (child_job_id);
create index task_job_links_parent_task_id
    on task_processor.task_job_links (parent_task_id);
create index task_job_links_parent_job_id
    on task_processor.task_job_links (parent_job_id);
