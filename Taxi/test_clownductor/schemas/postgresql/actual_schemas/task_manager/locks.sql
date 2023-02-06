create table task_manager.locks (
    name text unique primary key,
    job_id integer
);
