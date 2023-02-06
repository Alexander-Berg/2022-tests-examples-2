BEGIN TRANSACTION;

DROP TYPE IF EXISTS TARGET_STATE CASCADE;
CREATE TYPE TARGET_STATE AS ENUM (
    'OK', 'WARN', 'CRIT'
    );

DROP TABLE IF EXISTS test_data CASCADE;
CREATE TABLE test_data(
    test_id SERIAL PRIMARY KEY,
    schema_id TEXT NOT NULL,
    out_point_id TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    precedent_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    target_state TARGET_STATE,
    data JSONB NOT NULL,
    meta JSONB NOT NULL DEFAULT '{}',
    is_enabled BOOLEAN NOT NULL DEFAULT false,
    -- is_enabled => has target_state
    CHECK ((NOT is_enabled) OR (target_state IS NOT null))
);
CREATE INDEX test_data_schema_id_index
    ON test_data(schema_id);

COMMIT TRANSACTION;
