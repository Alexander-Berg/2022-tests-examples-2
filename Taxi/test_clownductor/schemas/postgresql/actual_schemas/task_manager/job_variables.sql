create table task_manager.job_variables (
    -- job id associated with these variables
    job_id integer unique not null references
        task_manager.jobs (id) on delete cascade,
    -- json-encoded dict variables
    variables text not null default '{}'
);
