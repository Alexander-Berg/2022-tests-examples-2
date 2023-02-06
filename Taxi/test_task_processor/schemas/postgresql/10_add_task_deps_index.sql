create index concurrently task_processor_task_deps_next_task_id
    on task_processor.task_deps (next_task_id);
