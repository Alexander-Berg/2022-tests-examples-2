BEGIN TRANSACTION;

CREATE SCHEMA distlocks;

CREATE SEQUENCE distlocks.fencing_token_seq START 1;

CREATE TABLE distlocks.namespaces (
    name TEXT PRIMARY KEY,
    created TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
);

CREATE TABLE distlocks.locks (
    namespace_name TEXT NOT NULL REFERENCES distlocks.namespaces(name),
    name TEXT NOT NULL,
    PRIMARY KEY (namespace_name, name),
    owner TEXT NOT NULL,
    expiration_time TIMESTAMP NOT NULL,
    fencing_token BIGSERIAL NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    updated TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
);

COMMIT TRANSACTION;
