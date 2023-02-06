CREATE SCHEMA qc_photo;

CREATE TABLE qc_photo.tasks (
    id BIGSERIAL PRIMARY KEY,
    type TEXT,
    name TEXT,
    description TEXT,
    storage_type TEXT
);

CREATE TABLE qc_photo.subtasks (
    id BIGSERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES qc_photo.tasks(id),
    type TEXT,
    name TEXT,
    description TEXT,
    path_to_example_image TEXT
);

CREATE TABLE qc_photo.received_photo_logs (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    utc_created_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),

    session_id TEXT,
    telegram_id BIGINT,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    language_code TEXT,

    bot_id BIGINT,
    is_bot BOOLEAN,

    group_id BIGINT, -- Аватарница mds group_id
    file_name_local TEXT ,
    file_path_local TEXT,
    file_path_mds TEXT,
    storage_type TEXT,

    -- telegram api related responses
    file_id TEXT,
    file_size INTEGER,
    file_height INTEGER,
    file_width INTEGER,

    task_type TEXT,
    task_id INTEGER REFERENCES qc_photo.tasks(id),

    subtask_type TEXT,
    subtask_id INTEGER REFERENCES qc_photo.subtasks(id)
);
