DROP TABLE IF EXISTS "taxi_db_postgres_atlas_backend"."distlock";

CREATE TABLE IF NOT EXISTS "taxi_db_postgres_atlas_backend"."distlock"
(
    task_name TEXT NOT NULL UNIQUE,
    creation_time TIMESTAMP NOT NULL default NOW()
);
