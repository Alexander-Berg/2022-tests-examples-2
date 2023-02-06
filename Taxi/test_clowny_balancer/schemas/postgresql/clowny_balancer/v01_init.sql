CREATE SCHEMA balancers;

CREATE FUNCTION balancers.set_updated() RETURNS TRIGGER AS $set_updated$
    BEGIN
        IF NEW.updated_at IS NULL THEN NEW.updated_at = NOW(); END IF;
        RETURN NEW;
    END;
$set_updated$ LANGUAGE plpgsql;

CREATE FUNCTION balancers.set_deleted() RETURNS TRIGGER AS $set_deleted$
    BEGIN
        IF NEW.is_deleted AND NOT OLD.is_deleted THEN NEW.deleted_at = NOW(); END IF;
        IF NOT NEW.is_deleted AND OLD.is_deleted THEN NEW.deleted_at = NULL; END IF;
        RETURN NEW;
    END;
$set_deleted$ LANGUAGE plpgsql;

CREATE TYPE balancers.namespace_env_t AS ENUM (
    'testing',  -- unstable included
    'stable'  -- pre_stable included
);

CREATE TABLE balancers.namespaces (
    -- common
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,

    -- references
    project_id INTEGER NOT NULL,
    awacs_namespace TEXT NOT NULL,
    env balancers.namespace_env_t NOT NULL,
    abc_quota_source TEXT NOT NULL,

    -- own
    is_shared BOOL NOT NULL DEFAULT FALSE,
    is_external BOOL NOT NULL DEFAULT FALSE,

    -- disallow creating shared external namespaces
    CHECK ( NOT (is_shared AND is_external) ),
    -- deleted items cant be without delete time
    CHECK ( is_deleted <> (deleted_at IS NULL) )
);

CREATE UNIQUE INDEX uniq_non_deleted_awacs_namespace_idx
    ON balancers.namespaces(awacs_namespace) WHERE NOT is_deleted;

CREATE TRIGGER balancers_namespaces_set_updated BEFORE UPDATE OR INSERT ON balancers.namespaces
    FOR EACH ROW EXECUTE PROCEDURE balancers.set_updated();
CREATE TRIGGER balancers_namespaces_set_deleted BEFORE UPDATE ON balancers.namespaces
    FOR EACH ROW EXECUTE PROCEDURE balancers.set_deleted();

CREATE TYPE balancers.entry_point_env_t AS ENUM (
    'unstable',
    'testing',
    'prestable',
    'stable'
);
CREATE TYPE balancers.entry_point_protocol_t AS ENUM (
    'http',
    'https'
);

CREATE TABLE balancers.entry_points (
    -- common
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,

    -- references
    namespace_id INTEGER REFERENCES balancers.namespaces(id) ON DELETE CASCADE NOT NULL,
    awacs_upstream_id TEXT NOT NULL,

    -- own
    is_external BOOL NOT NULL DEFAULT FALSE,
    can_share_namespace BOOL NOT NULL DEFAULT FALSE,

    protocol balancers.entry_point_protocol_t NOT NULL,
    dns_name TEXT NOT NULL,
    env balancers.entry_point_env_t NOT NULL,

    -- disallow external to be sharable
    CHECK ( NOT (is_external AND can_share_namespace) ),
    -- disallow non https for external
    CHECK ( NOT (is_external AND protocol != 'https') ),
    -- deleted items cant be without delete time
    CHECK ( is_deleted <> (deleted_at IS NULL) )
);

CREATE UNIQUE INDEX uniq_non_deleted_dns_name_awacs_upstream_id_idx
    ON balancers.entry_points(dns_name, awacs_upstream_id) WHERE NOT is_deleted;

CREATE TRIGGER balancers_entry_points_set_updated BEFORE UPDATE OR INSERT ON balancers.entry_points
    FOR EACH ROW EXECUTE PROCEDURE balancers.set_updated();
CREATE TRIGGER balancers_entry_points_set_deleted BEFORE UPDATE ON balancers.entry_points
    FOR EACH ROW EXECUTE PROCEDURE balancers.set_deleted();

CREATE TYPE balancers.upstream_env_t AS ENUM (
    'unstable',
    'testing',
    'prestable',
    'stable'
);

CREATE TABLE balancers.upstreams (
    -- common
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,

    -- references
    branch_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    awacs_backend_id TEXT NOT NULL,

    -- own
    env balancers.upstream_env_t NOT NULL,

    UNIQUE (branch_id, service_id, awacs_backend_id),
    -- deleted items cant be without delete time
    CHECK ( is_deleted <> (deleted_at IS NULL) )
);

CREATE UNIQUE INDEX uniq_non_deleted_branch_id_idx
    ON balancers.upstreams(branch_id) WHERE NOT is_deleted;

CREATE TRIGGER balancers_upstreams_set_updated BEFORE UPDATE OR INSERT ON balancers.upstreams
    FOR EACH ROW EXECUTE PROCEDURE balancers.set_updated();
CREATE TRIGGER balancers_upstreams_set_deleted BEFORE UPDATE ON balancers.upstreams
    FOR EACH ROW EXECUTE PROCEDURE balancers.set_deleted();

CREATE TABLE balancers.entry_points_upstreams (
    id SERIAL PRIMARY KEY,
    entry_point_id INTEGER REFERENCES balancers.entry_points(id) NOT NULL,
    upstream_id INTEGER REFERENCES balancers.upstreams(id) NOT NULL,

    UNIQUE (entry_point_id, upstream_id)
);
