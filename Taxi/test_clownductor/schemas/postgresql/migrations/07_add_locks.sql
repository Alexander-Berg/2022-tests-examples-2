CREATE TABLE task_manager.locks (
    name TEXT UNIQUE PRIMARY KEY,
    job_id INTEGER
);
