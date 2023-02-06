BEGIN;

DROP TABLE IF EXISTS alert_manager.branch_juggler_host;
DROP TABLE IF EXISTS alert_manager.juggler_host;

CREATE TABLE alert_manager.juggler_host (
    id BIGSERIAL PRIMARY KEY,
    juggler_host VARCHAR NOT NULL,

    UNIQUE(juggler_host)
);

CREATE TABLE alert_manager.branch_juggler_host (
    id BIGSERIAL PRIMARY KEY,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    clown_branch_id BIGINT NOT NULL,
    juggler_host_id BIGINT NOT NULL REFERENCES alert_manager.juggler_host (id)
);

CREATE UNIQUE INDEX branch_juggler_host_clown_branch_id_key
    ON alert_manager.branch_juggler_host(clown_branch_id)
    WHERE deleted_at IS NULL;

CREATE TRIGGER alert_manager_branch_juggler_host_set_updated
    BEFORE UPDATE
    ON alert_manager.branch_juggler_host
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();

COMMIT;
