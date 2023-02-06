create table task_manager.jobs (
    -- just a unique identifier
    id serial unique primary key,
    -- service id associated with the job
    service_id integer not null references
        clownductor.services (id) on delete cascade,
    -- branch id associated with the job (or null for service-level jobs)
    branch_id integer default null references
        clownductor.branches (id) on delete cascade,
    -- name of the recipe
    name text,
    -- login of the author
    initiator text,
    -- current job status
    status job_status default 'in_progress'::job_status,
    -- creation time
    created_at integer default extract (epoch from now()),
    -- reason for error or cancelation
    error_message text default null,
    -- finish time
    finished_at integer default null,
    idempotency_token text default null,
    tp_change_doc_id text default null,
    remote_job_id integer default null,
    tp_token text unique default null,
    change_doc_id text default null,
    real_time integer,
    total_time integer
);

create index task_manager_jobs_service_id_branch_id
    on task_manager.jobs (service_id, branch_id);
create index task_manager_jobs_status
    on task_manager.jobs (status);
create unique index concurrently task_manager_jobs_token_unique
    on task_manager.jobs (idempotency_token);
create unique index change_doc_id_key
    on task_manager.jobs(change_doc_id)
where status = 'in_progress' and change_doc_id is not null;
