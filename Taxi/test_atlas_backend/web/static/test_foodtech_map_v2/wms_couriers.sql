CREATE TABLE IF NOT EXISTS "taxi_db_postgres_atlas_backend"."wms_couriers"
(
    courier_id TEXT PRIMARY KEY,
    courier_external_id TEXT,
    name TEXT,
    source TEXT,
    status TEXT,
    free_time NUMERIC,
    shift_type TEXT,
    updated_at TIMESTAMP NOT NULL
);
