DROP SCHEMA IF EXISTS personal_export CASCADE;

CREATE SCHEMA personal_export;

CREATE TYPE personal_export.export_status AS ENUM (
    'ready',
    'in_progress',
    'need_retry',
    'need_post_msg',
    'finished'
);

CREATE TABLE personal_export.export_info(
    id SERIAL PRIMARY KEY,
    yandex_login TEXT NOT NULL,
    ticket TEXT NOT NULL,
    input_yt_table  TEXT NOT NULL,
    output_table_ttl INTEGER NOT NULL,
    need_duplicate_columns BOOLEAN  NOT NULL DEFAULT TRUE,
    show_export_status_column BOOLEAN  NOT NULL DEFAULT FALSE,
    status personal_export.export_status NOT NULL DEFAULT 'ready'::personal_export.export_status,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE personal_export.export_columns_data(
    id SERIAL PRIMARY KEY,
    export_type TEXT NOT NULL,
    data_type  TEXT NOT NULL,
    yt_column_name  TEXT NOT NULL,
    export_id INT NOT NULL,
    FOREIGN KEY (export_id) REFERENCES personal_export.export_info(id)
);

CREATE SCHEMA yt_export;

CREATE TABLE yt_export.last_synced_created_time(
    data_type TEXT PRIMARY KEY,
    last_created TIMESTAMPTZ NOT NULL
)
