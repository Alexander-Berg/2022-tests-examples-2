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
    updated_at integer not null
);

create table task_processor.recipes (
    id serial unique primary key,
    name text not null,
    provider_id integer not null references task_processor.providers (id),
    created_at integer not null default extract (epoch from now()),
    updated_at integer not null default extract (epoch from now()),
    job_vars jsonb not null default '[]'::jsonb, -- list required fields in job_variables for create_job

    unique (provider_id, name)
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

    unique (provider_id, name)
);

-- relationship recipes & cubes
create table task_processor.recipes_cubes (
    id serial unique primary key,
    recipe_id integer not null references task_processor.recipes (id),
    cube_id integer not null references task_processor.cubes (id),
    created_at integer default extract (epoch from now()),
    updated_at integer not null,
    next_id integer references task_processor.recipes_cubes (id),
    input jsonb default '{}'::jsonb, -- startup input_mapping for init task
    output jsonb default '{}'::jsonb --startup output_mapping for init task
);

create index task_processor_recipes_cubes_recipe_id
    on task_processor.recipes_cubes (recipe_id);
create index task_processor_recipes_cubes_cube_id
    on task_processor.recipes_cubes (cube_id);
create unique index task_processor_recipes_cubes_recipe_id_cube_id
 on task_processor.recipes_cubes (recipe_id, cube_id, next_id);

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
    idempotency_token text
);

create index task_processor_recipe_id on task_processor.jobs (recipe_id);
create index task_processor_jobs_status on task_processor.jobs (status);
create index task_processor_idempotency_token
    on task_processor.jobs (idempotency_token);

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
    optional_parameters jsonb default  '[]'::jsonb
);

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

create table task_processor.locks (
    name text unique primary key,
    job_id integer references task_processor.jobs (id)
);
