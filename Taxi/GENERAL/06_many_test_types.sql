BEGIN TRANSACTION;

DROP TABLE IF EXISTS persey_labs.lab_entity_tests, persey_labs.shift_tests;

-- table with lab_entities tests
CREATE TABLE persey_labs.lab_entity_tests(
    id SERIAL PRIMARY KEY,
    lab_entity_id VARCHAR NOT NULL REFERENCES persey_labs.lab_entities (id) ON DELETE CASCADE,
    -- test_id from config
    test_id TEXT NOT NULL,

    UNIQUE (lab_entity_id, test_id)
);

-- table with shifts tests
CREATE TABLE persey_labs.shift_tests(
    id SERIAL PRIMARY KEY,
    shift_id INTEGER NOT NULL REFERENCES persey_labs.lab_employee_shifts (id) ON DELETE CASCADE,
    -- test_id from config (consistency with lab entity provided on code level)
    test_id TEXT NOT NULL,

    UNIQUE (shift_id, test_id)
);

COMMIT TRANSACTION;
