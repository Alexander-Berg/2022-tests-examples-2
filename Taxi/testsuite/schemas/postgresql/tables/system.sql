CREATE TABLE access_control.system
(
    id         SERIAL      NOT NULL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    name       TEXT        NOT NULL UNIQUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_updated_at_timestamp
    BEFORE UPDATE ON access_control.system
    FOR EACH ROW
EXECUTE PROCEDURE trigger_set_updated_at_timestamp();
