create table if not exists task_manager.tasks (
    -- just a unique identifier
    id serial unique primary key,
    -- what job this task belongs to
    job_id integer not null references
        task_manager.jobs (id) on delete cascade,
    -- name of the cube used for this task
    name text not null,
    -- until what time we do not want to pay attention to this task
    sleep_until integer default 0,
    -- json-encoded mapping of the job variables to task's variables
    input_mapping text,
    -- json-encoded mapping of the task payload content to job variables
    output_mapping text,
    -- arbitrary json-encoded data used as a task state
    payload text default '{}',
    -- amount of successive retries made because of internal errors
    retries integer default 0,
    -- status of the task
    status job_status default 'in_progress'::job_status,
    -- reason for error or cancelation
    error_message text default null,
    -- unix-timestamp of creation time
    created_at integer default extract (epoch from now()),
    -- unix-timestamp of last update time
    updated_at integer not null default extract (epoch from now()),
    continue_at integer,
    started_at integer default null,
    real_time integer default null,
    total_time integer default null
);

create index task_manager_tasks_job_id
    on task_manager.tasks (job_id);
create index task_manager_tasks_sleep_until_status
    on task_manager.tasks (status, sleep_until);
create index task_manager_tasks_status_updated_at
    on task_manager.tasks (status, updated_at);

create table if not exists task_manager.task_deps (
    -- identifier of the "previous" task
    prev_task_id integer not null references
        task_manager.tasks (id) on delete cascade,
    -- identifier of the "next" task
    next_task_id integer not null references
        task_manager.tasks (id) on delete cascade,

    unique (prev_task_id, next_task_id)
);
