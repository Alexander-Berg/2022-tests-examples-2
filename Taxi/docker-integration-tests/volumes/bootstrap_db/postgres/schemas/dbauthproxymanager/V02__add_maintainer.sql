ALTER TABLE authproxy_manager.rules
    ADD COLUMN maintained_by TEXT;

CREATE TYPE authproxy_manager.rule_v2 AS (
    proxy TEXT,
    name TEXT,
    priority INTEGER,
    description TEXT,
	maintained_by TEXT,
    prefix TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    data JSONB
);
