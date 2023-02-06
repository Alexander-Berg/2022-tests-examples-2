create index concurrently task_manager_task_deps_next_task_id
    on task_manager.task_deps (next_task_id);
