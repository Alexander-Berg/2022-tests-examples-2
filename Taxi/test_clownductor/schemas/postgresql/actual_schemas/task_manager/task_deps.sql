create table if not exists task_manager.task_deps (
    -- identifier of the "previous" task
    prev_task_id integer not null references
        task_manager.tasks (id) on delete cascade,
    -- identifier of the "next" task
    next_task_id integer not null references
        task_manager.tasks (id) on delete cascade,

    unique (prev_task_id, next_task_id)
);

create index concurrently task_manager_task_deps_next_task_id
    on task_manager.task_deps (next_task_id);
