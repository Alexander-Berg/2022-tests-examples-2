CREATE SCHEMA dashboards;

-- Triggers

CREATE FUNCTION dashboards.set_updated() RETURNS TRIGGER
    AS $set_updated$
BEGIN
    NEW.updated_at := NOW() AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$set_updated$ LANGUAGE plpgsql;

CREATE FUNCTION dashboards.set_deleted() RETURNS TRIGGER
    AS $set_deleted$
BEGIN
    IF NEW.is_deleted AND NOT OLD.is_deleted THEN
        NEW.deleted_at = NOW() AT TIME ZONE 'UTC';
    END IF;
    IF NOT NEW.is_deleted AND OLD.is_deleted THEN
        NEW.deleted_at = NULL;
    END IF;
    RETURN NEW;
END;
$set_deleted$ LANGUAGE plpgsql;

CREATE FUNCTION dashboards.increment_version() RETURNS TRIGGER
    AS $increment_version$
BEGIN
    NEW.version := OLD.version + 1;
    RETURN NEW;
END;
$increment_version$ LANGUAGE plpgsql;


-- Common types

CREATE TYPE dashboards.http_method_e AS ENUM (
    'GET', 'PUT', 'POST', 'PATCH', 'DELETE', 'OPTIONS'
);

-- Service Branches

CREATE TYPE dashboards.service_group_type_e AS ENUM (
    'nanny',
    'conductor'
);

CREATE TYPE dashboards.service_group_info_t AS (
    name TEXT,
    type dashboards.service_group_type_e
);

CREATE DOMAIN dashboards.response_http_status_t AS INT
    not null
    check (value >= 400 and value <= 599)
;

CREATE TYPE dashboards.custom_response_t AS (
    status dashboards.response_http_status_t,
    description text
);

CREATE TABLE dashboards.service_branches (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    -- Relates 1-1 to branch_id in clownductor
    clown_branch_id INTEGER NOT NULL CHECK ( clown_branch_id > 0 ),
    project_name TEXT NOT NULL,
    service_name TEXT NOT NULL,
    branch_name TEXT NOT NULL,
    group_info dashboards.service_group_info_t NOT NULL,
    hostnames TEXT[] NOT NULL DEFAULT '{}'::TEXT[] CHECK ( NOT '' = ANY(hostnames) ),

    awacs_namespace TEXT DEFAULT NULL,

    CONSTRAINT deleted_without_delete_time CHECK ( is_deleted <> (deleted_at IS NULL) )
);

CREATE UNIQUE INDEX uniq_non_deleted_service_branch_idx
    ON dashboards.service_branches(clown_branch_id)
    WHERE NOT is_deleted;
CREATE TRIGGER dashboards_service_branches_set_updated
    BEFORE UPDATE
    ON dashboards.service_branches
    FOR EACH ROW EXECUTE PROCEDURE dashboards.set_updated();
CREATE TRIGGER dashboards_service_branches_set_deleted
    BEFORE UPDATE
    ON dashboards.service_branches
    FOR EACH ROW EXECUTE PROCEDURE dashboards.set_deleted();


-- Handlers

CREATE TABLE dashboards.handlers (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    service_branch_id BIGINT NOT NULL
        REFERENCES dashboards.service_branches(id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL CHECK ( length(endpoint) > 0 ),
    method dashboards.http_method_e NOT NULL,

    description TEXT DEFAULT NULL,
    custom_responses dashboards.custom_response_t[]
        NOT NULL DEFAULT '{}'::dashboards.custom_response_t[],
    has_path_params BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE UNIQUE INDEX uniq_endpoint_method_handler_per_branch_idx
    ON dashboards.handlers(service_branch_id, endpoint, method)
    WHERE NOT is_deleted;
CREATE TRIGGER dashboards_handlers_set_updated
    BEFORE UPDATE
    ON dashboards.handlers
    FOR EACH ROW EXECUTE PROCEDURE dashboards.set_updated();
CREATE TRIGGER dashboards_handlers_set_deleted
    BEFORE UPDATE
    ON dashboards.handlers
    FOR EACH ROW EXECUTE PROCEDURE dashboards.set_deleted();


-- Configs

CREATE TYPE dashboards.config_status_e AS ENUM (
-- in progress statuses
    'waiting',
    'applying',
-- terminal statuses
    'applied',
    'failed'
);

CREATE TYPE dashboards.layout_t AS (
    name TEXT,
    parameters JSONB
);

CREATE TABLE dashboards.configs (
    id BIGSERIAL PRIMARY KEY,
    version SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    dashboard_name TEXT NOT NULL,
    status dashboards.config_status_e NOT NULL,

    layouts dashboards.layout_t[] NOT NULL
        CONSTRAINT non_empty_layouts CHECK ( array_length(layouts, 1) > 0 ),

    dorblu_custom TEXT DEFAULT NULL,

    -- apply config related info
    start_apply_time TIMESTAMP DEFAULT NULL,
    finish_apply_time TIMESTAMP DEFAULT NULL,
    job_id INTEGER DEFAULT NULL CHECK ( job_id > 0 )
);

CREATE UNIQUE INDEX uniq_dashboard_name_per_status_idx
    ON dashboards.configs(dashboard_name, status)
    WHERE NOT is_deleted;
CREATE TRIGGER dashboards_configs_increment_version
    BEFORE UPDATE
    ON dashboards.configs
    FOR EACH ROW EXECUTE PROCEDURE dashboards.increment_version();
CREATE TRIGGER dashboards_configs_set_updated
    BEFORE UPDATE
    ON dashboards.configs
    FOR EACH ROW EXECUTE PROCEDURE dashboards.set_updated();
CREATE TRIGGER dashboards_configs_set_deleted
    BEFORE UPDATE
    ON dashboards.configs
    FOR EACH ROW EXECUTE PROCEDURE dashboards.set_deleted();

CREATE TABLE dashboards.branches_configs_link (
    service_branch_id BIGINT NOT NULL
        REFERENCES dashboards.service_branches(id) ON DELETE CASCADE,
    config_id BIGINT NOT NULL
        REFERENCES dashboards.configs(id) ON DELETE CASCADE,

    PRIMARY KEY (service_branch_id, config_id)
);

CREATE TABLE dashboards.configs_handlers_link (
    id BIGSERIAL PRIMARY KEY,
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    config_id BIGINT NOT NULL REFERENCES dashboards.configs(id) ON DELETE CASCADE,
    handler_id BIGINT NOT NULL REFERENCES dashboards.handlers(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX uniq_non_deleted_configs_handlers_link_idx
    ON dashboards.configs_handlers_link(config_id, handler_id)
    WHERE NOT is_deleted;
CREATE TRIGGER dashboards_configs_handlers_link_set_deleted
    BEFORE UPDATE
    ON dashboards.configs_handlers_link
    FOR EACH ROW EXECUTE PROCEDURE dashboards.set_deleted();

CREATE TYPE dashboards.config_upload_status_e AS ENUM (
-- in progress statuses
    'waiting',
    'applying',
-- terminal statuses
    'applied'
);

CREATE TYPE dashboards.config_upload_vendor_e AS ENUM (
    'github',
    'arcadia'
);

CREATE TABLE dashboards.configs_upload (
    id BIGSERIAL PRIMARY KEY,
    job_idempotency_key TEXT,
    status dashboards.config_upload_status_e NOT NULL,
    vendor dashboards.config_upload_vendor_e NOT NULL,
    content TEXT NOT NULL,
    filepath TEXT NOT NULL
);

CREATE UNIQUE INDEX configs_upload_filepath_vendor_unique
    ON dashboards.configs_upload(filepath, vendor);

CREATE INDEX configs_upload_status_vendor
    ON dashboards.configs_upload(status, vendor);
