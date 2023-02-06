drop index concurrently if exists task_manager.task_manager_jobs_token;
create unique index concurrently task_manager_jobs_token_unique
    on task_manager.jobs (idempotency_token);
