DROP SCHEMA IF EXISTS authproxy_manager CASCADE;

CREATE SCHEMA authproxy_manager;

--

CREATE TABLE authproxy_manager.rules (
    id BIGSERIAL PRIMARY KEY,
    proxy TEXT NOT NULL,
    name TEXT NOT NULL,
    priority INTEGER NOT NULL,
    description TEXT NOT NULL,
    prefix TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    data JSONB NOT NULL  -- arbitrary proxy-specific data
);

CREATE UNIQUE INDEX authproxy_rules_name ON
    authproxy_manager.rules(name);

CREATE UNIQUE INDEX authproxy_priority ON
    authproxy_manager.rules(name, priority);

CREATE TYPE authproxy_manager.rule_v1 AS (
    proxy TEXT,
    name TEXT,
    priority INTEGER,
    description TEXT,
    prefix TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    data JSONB
);
