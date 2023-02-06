CREATE SCHEMA quotas;

CREATE TABLE quotas.quotas (
    -- common
    ts TIMESTAMP DEFAULT NOW(),
    resource_provider TEXT NOT NULL,
    data jsonb
);
