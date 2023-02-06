create index task_manager_tasks_status_updated_at
    on task_manager.tasks (status, updated_at);
