ALTER TABLE supportai.configuration_test ADD COLUMN chat_id TEXT;

CREATE TABLE IF NOT EXISTS supportai.testing_aggregation
(
    id SERIAL PRIMARY KEY,
    task_id INT UNIQUE NOT NULL REFERENCES supportai.tasks(id),
    ok_chat_count INT,
    chat_count INT,
    equal_count INT,
    topic_ok_count_v1 INT,
    topic_ok_count_v2 INT,
    reply_count_v1 INT,
    reply_count_v2 INT,
    close_count_v1 INT,
    close_count_v2 INT,
    reply_or_close_count_v1 INT,
    reply_or_close_count_v2 INT,
    topic_details JSONB
);
