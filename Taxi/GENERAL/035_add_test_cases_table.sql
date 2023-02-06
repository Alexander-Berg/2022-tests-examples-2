BEGIN TRANSACTION;

DROP TABLE IF EXISTS test_cases CASCADE;
CREATE TABLE test_cases(
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL DEFAULT '',
    test_data_id INTEGER NOT NULL,
    schema_id TEXT NOT NULL,
    out_point_id TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    check_type TEXT NOT NULL,
    check_params JSONB NOT NULL DEFAULT '{}',
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE
);

DROP INDEX IF EXISTS test_cases_schema_id_index CASCADE;
CREATE INDEX test_cases_schema_id_index
    ON test_cases(schema_id);

COMMIT TRANSACTION;
