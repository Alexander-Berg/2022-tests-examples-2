CREATE TYPE access_control.storage_t AS ENUM ('body', 'query', 'path');

CREATE TABLE access_control.permission_calculation_rules
(
    id                 SERIAL                   NOT NULL PRIMARY KEY,
    system_id          INTEGER                  NOT NULL REFERENCES access_control.system (id) ON DELETE CASCADE,
    storage            access_control.storage_t NOT NULL,
    path               TEXT                     NOT NULL,
    version            INT                      NOT NULL,
    name               TEXT                     NOT NULL UNIQUE,
    created_at         TIMESTAMPTZ              NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ              NOT NULL DEFAULT NOW()
);

CREATE TRIGGER rules_set_updated_at_timestamp
    BEFORE UPDATE ON access_control.permission_calculation_rules
    FOR EACH ROW
EXECUTE PROCEDURE trigger_set_updated_at_timestamp();
