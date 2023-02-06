CREATE TABLE IF NOT EXISTS "taxi_db_postgres_atlas_backend"."calc_alternative_types"
(
    type_id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT
);

INSERT INTO "taxi_db_postgres_atlas_backend"."calc_alternative_types" (type_id, name)
    VALUES ('combo_outer', 'combo_outer');
