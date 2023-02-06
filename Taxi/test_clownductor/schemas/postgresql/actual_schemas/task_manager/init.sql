drop schema if exists task_manager;
create schema task_manager;

create type job_status as enum (
    'in_progress',
    'success',
    'failed',
    'canceled',
    'inited'
);
