CREATE TABLE IF NOT EXISTS supportai.configuration_test
(
    id SERIAL PRIMARY KEY,
    task_id INT NOT NULL REFERENCES supportai.tasks(id),
    request_text TEXT,
    is_equal BOOLEAN NOT NULL,
    diff JSONB
);
