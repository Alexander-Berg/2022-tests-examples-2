BEGIN TRANSACTION;

DROP TYPE IF EXISTS ALERT_STATUS CASCADE;
CREATE TYPE ALERT_STATUS AS ENUM (
		'OK', 'WARN', 'CRIT', 'NODATA', 'ERROR'
);

DROP TYPE IF EXISTS circuit_states_v1 CASCADE;
CREATE TYPE circuit_states_v1 AS(
    circuit_id TEXT,
    out_point_id TEXT,
    alert_status ALERT_STATUS,
    incident_start_time TIMESTAMP,
    updated TIMESTAMP,
    description TEXT
);

DROP TABLE IF EXISTS circuit_states CASCADE;
CREATE TABLE circuit_states(
    circuit_id TEXT,
    out_point_id TEXT,
    alert_status ALERT_STATUS NOT NULL,
    incident_start_time TIMESTAMP,
    updated TIMESTAMP NOT NULL,
    description TEXT NOT NULL,
    PRIMARY KEY (circuit_id, out_point_id)
);

DROP TYPE IF EXISTS incident_history_v1 CASCADE;
CREATE TYPE incident_history_v1 AS(
    circuit_id TEXT,
    out_point_id TEXT,
    incident_status TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    alert_status ALERT_STATUS,
    description TEXT
);

DROP TABLE IF EXISTS incident_history CASCADE;
CREATE TABLE incident_history(
    id SERIAL PRIMARY KEY,
    circuit_id TEXT NOT NULL,
    out_point_id TEXT NOT NULL,
    incident_status TEXT NOT NULL DEFAULT 'closed',
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    alert_status ALERT_STATUS NOT NULL,
    description TEXT NOT NULL
);

DROP TYPE IF EXISTS digest_v1 CASCADE;
CREATE TYPE digest_v1 AS(
    id INTEGER,
    digest_name TEXT,
    sticker_uid TEXT,
    last_broadcast TIMESTAMP,
    period_hours INTEGER
);

DROP TABLE IF EXISTS digests CASCADE;
CREATE TABLE digests(
    id SERIAL PRIMARY KEY,
    digest_name TEXT NOT NULL,
    sticker_uid TEXT NOT NULL,
    last_broadcast TIMESTAMP NOT NULL,
    period_hours INTEGER NOT NULL
);

DROP TYPE IF EXISTS digest_subscription_v1 CASCADE;
CREATE TYPE digest_subscription_v1 AS(
    digest_id INTEGER,
    circuit_id TEXT,
    out_point_id TEXT
);

DROP TABLE IF EXISTS digest_subscriptions CASCADE;
CREATE TABLE digest_subscriptions(
    digest_id INTEGER,
    circuit_id TEXT,
    out_point_id TEXT,
    PRIMARY KEY (digest_id, circuit_id, out_point_id)
);

DROP TYPE IF EXISTS circuit_out_point_id_v1 CASCADE;
CREATE TYPE circuit_out_point_id_v1 AS(
    circuit_id TEXT,
    out_point_id TEXT
);

DROP TABLE IF EXISTS distlock CASCADE;
CREATE TABLE distlock(
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);

DROP TYPE IF EXISTS service_v1 CASCADE;
CREATE TYPE service_v1 AS(
    id INTEGER,
    name TEXT,
    cluster_type TEXT,
    updated TIMESTAMPTZ
);

DROP TABLE IF EXISTS services CASCADE;
CREATE TABLE services(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cluster_type TEXT NOT NULL,
    updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX services_name_cluster_type_index
    ON services(name, cluster_type);
CREATE INDEX services_cluster_type_index
    ON services(cluster_type);
CREATE INDEX services_updated_index
    ON services(updated);

DROP TYPE IF EXISTS ENVIRONMENT CASCADE;
CREATE TYPE ENVIRONMENT AS ENUM (
    'unstable', 'testing', 'prestable', 'stable'
);

DROP TYPE IF EXISTS host_v1 CASCADE;
CREATE TYPE host_v1 AS(
    host_name TEXT,
    service_id INTEGER,
    environment ENVIRONMENT
);

DROP TABLE IF EXISTS hosts CASCADE;
CREATE TABLE hosts(
    host_name TEXT PRIMARY KEY,
    service_id INTEGER NOT NULL,
    environment ENVIRONMENT NOT NULL
);
CREATE INDEX hosts_service_id_index
    ON hosts(service_id);
CREATE INDEX hosts_service_id_environment_index
    ON hosts(service_id, environment);

DROP TABLE IF EXISTS circuit_schemas CASCADE;
CREATE TABLE circuit_schemas(
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL DEFAULT '',
    circuit_schema JSONB NOT NULL,
    updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revision SERIAL
);
CREATE INDEX circuit_schemas_updated_index
    ON circuit_schemas(revision);

DROP TYPE IF EXISTS circuit_schema_v1 CASCADE;
CREATE TYPE circuit_schema_v1 AS(
    id TEXT,
    description TEXT,
    circuit_schema JSONB,
    updated TIMESTAMPTZ,
    revision INTEGER
);

ALTER TABLE digests
    ADD COLUMN digest_format TEXT NOT NULL DEFAULT 'incident_list';

DROP TYPE IF EXISTS digest_v2 CASCADE;
CREATE TYPE digest_v2 AS(
    id INTEGER,
    digest_name TEXT,
    sticker_uid TEXT,
    last_broadcast TIMESTAMP,
    period_hours INTEGER,
    digest_format TEXT
);

ALTER TABLE hosts
    ADD COLUMN branch_direct_link TEXT;

DROP TYPE IF EXISTS host_v1 CASCADE;
CREATE TYPE host_v1 AS(
    host_name TEXT,
    service_id INTEGER,
    environment ENVIRONMENT,
    branch_direct_link TEXT
);

ALTER TABLE circuit_states
    ADD COLUMN meta_data jsonb;

ALTER TABLE incident_history
    ADD COLUMN meta_data jsonb;

DROP TYPE IF EXISTS circuit_states_v2 CASCADE;
CREATE TYPE circuit_states_v2 AS(
    circuit_id TEXT,
    out_point_id TEXT,
    alert_status ALERT_STATUS,
    incident_start_time TIMESTAMP,
    updated TIMESTAMP,
    description TEXT,
    meta_data JSONB
);

DROP TYPE IF EXISTS incident_history_v2 CASCADE;
CREATE TYPE incident_history_v2 AS(
    circuit_id TEXT,
    out_point_id TEXT,
    incident_status TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    alert_status ALERT_STATUS,
    description TEXT,
    meta_data JSONB
);

ALTER TABLE services
    ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT FALSE;

DROP TYPE IF EXISTS service_v2 CASCADE;
CREATE TYPE service_v2 AS(
    id INTEGER,
    name TEXT,
    cluster_type TEXT,
    updated TIMESTAMPTZ,
    deleted BOOLEAN
);

ALTER TABLE services
    ADD COLUMN project_id INTEGER NOT NULL DEFAULT -1,
    ADD COLUMN project_name TEXT NOT NULL DEFAULT 'no_project',
    ADD COLUMN maintainers TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN chief TEXT;

DROP TYPE IF EXISTS service_v3 CASCADE;
CREATE TYPE service_v3 AS(
    id INTEGER,
    name TEXT,
    cluster_type TEXT,
    updated TIMESTAMPTZ,
    deleted BOOLEAN,
    project_id INTEGER,
    project_name TEXT,
    maintainers TEXT[],
    chief TEXT
);

ALTER TABLE digests
    ADD COLUMN description TEXT;

DROP TYPE IF EXISTS digest_v3 CASCADE;
CREATE TYPE digest_v3 AS(
    id INTEGER,
    digest_name TEXT,
    sticker_uid TEXT,
    last_broadcast TIMESTAMP,
    period_hours INTEGER,
    digest_format TEXT,
    description TEXT
);

ALTER TABLE digests
    ADD COLUMN circuit_id_like TEXT,
    ADD COLUMN out_point_id_like TEXT;

DROP TYPE IF EXISTS digest_v4 CASCADE;
CREATE TYPE digest_v4 AS(
    id INTEGER,
    digest_name TEXT,
    sticker_uid TEXT,
    last_broadcast TIMESTAMP,
    period_hours INTEGER,
    digest_format TEXT,
    description TEXT,
    circuit_id_like TEXT,
    out_point_id_like TEXT
);

ALTER TABLE services
    ADD COLUMN grafana_url TEXT;

DROP TYPE IF EXISTS service_v4 CASCADE;
CREATE TYPE service_v4 AS(
    id INTEGER,
    name TEXT,
    cluster_type TEXT,
    updated TIMESTAMPTZ,
    deleted BOOLEAN,
    project_id INTEGER,
    project_name TEXT,
    maintainers TEXT[],
    chief TEXT,
    grafana_url TEXT
);

DROP TYPE IF EXISTS digest_v5 CASCADE;
CREATE TYPE digest_v5 AS(
    id INTEGER,
    digest_name TEXT,
    sticker_uid TEXT,
    last_broadcast TIMESTAMP,
    period_hours INTEGER,
    digest_format TEXT,
    description TEXT,
    circuit_id_like TEXT,
    out_point_id_like TEXT,
    params JSONB
    );

ALTER TABLE digests
    ADD COLUMN params JSONB not null default '{}';

DROP TYPE IF EXISTS branch_v1 CASCADE;
CREATE TYPE branch_v1 AS(
    id INTEGER,
    service_id INTEGER,
    env ENVIRONMENT,
    direct_link TEXT
);
DROP TABLE IF EXISTS branches CASCADE;
CREATE TABLE branches(
    id INTEGER PRIMARY KEY,
    service_id INTEGER NOT NULL,
    env ENVIRONMENT NOT NULL,
    direct_link TEXT
);
DROP INDEX IF EXISTS branches_service_id_index CASCADE;
CREATE INDEX branches_service_id_index
    ON branches(service_id);

DROP TYPE IF EXISTS branch_domain_v1 CASCADE;
CREATE TYPE branch_domain_v1 AS(
    branch_id INTEGER,
    solomon_object TEXT,
    name TEXT
);
DROP TABLE IF EXISTS branch_domains CASCADE;
CREATE TABLE branch_domains(
    branch_id INTEGER NOT NULL,
    solomon_object TEXT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (branch_id, solomon_object)
);
DROP INDEX IF EXISTS branch_domains_branch_id_index CASCADE;
CREATE INDEX branch_domains_branch_id_index
    ON branch_domains(branch_id);

DROP TYPE IF EXISTS branch_host_v1 CASCADE;
CREATE TYPE branch_host_v1 AS(
    host_name TEXT,
    branch_id INTEGER
);
DROP TABLE IF EXISTS branch_hosts CASCADE;
CREATE TABLE branch_hosts(
    host_name TEXT PRIMARY KEY,
    branch_id INTEGER NOT NULL
);

DROP TYPE IF EXISTS TARGET_STATE CASCADE;
CREATE TYPE TARGET_STATE AS ENUM (
    'OK', 'WARN', 'CRIT'
    );

DROP TABLE IF EXISTS test_data CASCADE;
CREATE TABLE test_data(
    test_id SERIAL PRIMARY KEY,
    schema_id TEXT NOT NULL,
    out_point_id TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    precedent_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    target_state TARGET_STATE,
    data JSONB NOT NULL,
    meta JSONB NOT NULL DEFAULT '{}',
    is_enabled BOOLEAN NOT NULL DEFAULT false,
    -- is_enabled => has target_state
    CHECK ((NOT is_enabled) OR (target_state IS NOT null))
);
CREATE INDEX test_data_schema_id_index
    ON test_data(schema_id);

-- move grafana_url from service to branch

ALTER TABLE branches
    ADD COLUMN grafana_url TEXT;

UPDATE branches SET grafana_url = (
    SELECT grafana_url FROM services
        WHERE branches.service_id = services.id
          AND (branches.env = 'stable' OR branches.env = 'prestable')
);

DROP TYPE IF EXISTS branch_v2 CASCADE;
CREATE TYPE branch_v2 AS(
    id INTEGER,
    service_id INTEGER,
    env ENVIRONMENT,
    direct_link TEXT,
    grafana_url TEXT
);

DROP TYPE IF EXISTS service_v5 CASCADE;
CREATE TYPE service_v5 AS(
    id INTEGER,
    name TEXT,
    cluster_type TEXT,
    updated TIMESTAMPTZ,
    deleted BOOLEAN,
    project_id INTEGER,
    project_name TEXT,
    maintainers TEXT[],
    chief TEXT
);

-- add service stats

DROP TABLE IF EXISTS service_stats CASCADE;
CREATE TABLE service_stats
(
    stat_id TEXT      NOT NULL,
    service_id    INTEGER   NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    updated       TIMESTAMP NOT NULL DEFAULT now(),
    stat_data          JSONB     NOT NULL,
    PRIMARY KEY (stat_id, service_id),
    CHECK (period_end > period_start)
);
DROP INDEX IF EXISTS service_stats_updated_index CASCADE;
CREATE INDEX service_stats_updated_index
    ON service_stats(updated);

DROP TYPE IF EXISTS service_stat_v1 CASCADE;
CREATE TYPE service_stat_v1 AS (
    stat_id TEXT,
    service_id INTEGER,
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    updated       TIMESTAMP,
    stat_data JSONB
);

-- add spec template mods

DROP TABLE IF EXISTS spec_template_mods CASCADE;
CREATE TABLE spec_template_mods(
    id SERIAL PRIMARY KEY,
    spec_template_id TEXT NOT NULL,
    service_id INTEGER,
    env ENVIRONMENT,
    host_name TEXT,
    domain_name TEXT,
    circuit_id TEXT,
    type TEXT NOT NULL,
    mod_data JSONB NOT NULL,
    revision SERIAL,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

DROP INDEX IF EXISTS spec_template_mod_relation_unique_index CASCADE;
CREATE UNIQUE INDEX spec_template_mod_relation_unique_index
    ON spec_template_mods(spec_template_id, service_id, env, host_name,
                          domain_name, circuit_id, type)
    WHERE (deleted = FALSE);

DROP TYPE IF EXISTS spec_template_mod_v1 CASCADE;
CREATE TYPE spec_template_mod_v1 AS(
    id INTEGER,
    spec_template_id TEXT,
    service_id INTEGER,
    env ENVIRONMENT,
    host_name TEXT,
    domain_name TEXT,
    circuit_id TEXT,
    type TEXT,
    mod_data JSONB,
    revision INTEGER,
    deleted BOOLEAN
);

-- add branch_name to branches table

ALTER TABLE branches
    ADD COLUMN branch_name TEXT NOT NULL DEFAULT '';

DROP TYPE IF EXISTS branch_v3 CASCADE;
CREATE TYPE branch_v3 AS(
                            id INTEGER,
                            service_id INTEGER,
                            env ENVIRONMENT,
                            direct_link TEXT,
                            grafana_url TEXT,
                            branch_name TEXT
                        );

-- add service_link to services table

ALTER TABLE services
    ADD COLUMN service_link TEXT NOT NULL DEFAULT '';

DROP TYPE IF EXISTS service_v6 CASCADE;
CREATE TYPE service_v6 AS(
                             id INTEGER,
                             name TEXT,
                             cluster_type TEXT,
                             updated TIMESTAMPTZ,
                             deleted BOOLEAN,
                             project_id INTEGER,
                             project_name TEXT,
                             maintainers TEXT[],
                             chief TEXT,
                             service_link TEXT
                         );

-- create change resource drafts

DROP TYPE IF EXISTS resource_type CASCADE;
CREATE TYPE resource_type AS ENUM (
    'cpu', 'ram', 'root_size', 'work_dir', 'instances', 'datacenters_count'
);

DROP TYPE IF EXISTS draft_approve_status CASCADE;
CREATE TYPE draft_approve_status AS ENUM (
    'no_decision', 'approved', 'rejected'
);

DROP TYPE IF EXISTS draft_apply_status CASCADE;
CREATE TYPE draft_apply_status AS ENUM (
    'not_started', 'in_progress', 'failed', 'succeeded'
);

DROP TYPE IF EXISTS resource_value CASCADE;
CREATE TYPE resource_value AS(
    resource resource_type,
    value INTEGER
);

DROP TYPE IF EXISTS change_resource_draft CASCADE;
CREATE TYPE change_resource_draft AS(
    id BIGINT,
    branch_id INTEGER,
    approve_status draft_approve_status,
    apply_status draft_apply_status,
    approve_status_age INTEGER,
    apply_status_age INTEGER,
    changes resource_value[]
);

DROP TABLE IF EXISTS change_resource_drafts CASCADE;
CREATE TABLE change_resource_drafts(
    id BIGINT PRIMARY KEY,
    branch_id INTEGER UNIQUE NOT NULL,
    approve_status draft_approve_status NOT NULL,
    apply_status draft_apply_status NOT NULL,
    approve_status_age INTEGER NOT NULL DEFAULT 0,
    apply_status_age INTEGER NOT NULL DEFAULT 0,
    changes resource_value[] NOT NULL
);

-- create applied drafts

DROP TABLE IF EXISTS applied_drafts CASCADE;
CREATE TABLE applied_drafts(
    id BIGINT PRIMARY KEY,
    url TEXT NOT NULL,
    move_to_applied_ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TYPE ENVIRONMENT ADD VALUE 'any';

COMMIT TRANSACTION;

BEGIN TRANSACTION;

ALTER TABLE spec_template_mods
    ALTER COLUMN service_id SET NOT NULL,
    ALTER COLUMN service_id SET DEFAULT -1,
    ALTER COLUMN env SET NOT NULL,
    ALTER COLUMN env SET DEFAULT 'any',
    ALTER COLUMN host_name SET NOT NULL,
    ALTER COLUMN host_name SET DEFAULT '',
    ALTER COLUMN domain_name SET NOT NULL,
    ALTER COLUMN domain_name SET DEFAULT '',
    ALTER COLUMN circuit_id SET NOT NULL,
    ALTER COLUMN circuit_id SET DEFAULT '',
    ADD COLUMN login TEXT NOT NULL DEFAULT 'not-specified',
    ADD COLUMN ticket TEXT NOT NULL DEFAULT 'INVALID',
    ADD COLUMN updated TIMESTAMPTZ NOT NULL DEFAULT now(),
    ADD CONSTRAINT spec_template_mods_unique UNIQUE (spec_template_id, service_id, env,
                host_name, domain_name, circuit_id);

DROP TYPE IF EXISTS spec_template_mod_v2 CASCADE;
CREATE TYPE spec_template_mod_v2 AS(
                                       id INTEGER,
                                       login TEXT,
                                       ticket TEXT,
                                       spec_template_id TEXT,
                                       service_id INTEGER,
                                       env ENVIRONMENT,
                                       host_name TEXT,
                                       domain_name TEXT,
                                       circuit_id TEXT,
                                       type TEXT,
                                       mod_data JSONB,
                                       revision INTEGER,
                                       deleted BOOLEAN,
                                       updated TIMESTAMPTZ
                                   );

ALTER TABLE spec_template_mods
    DROP CONSTRAINT IF EXISTS spec_template_mods_unique;
ALTER TABLE spec_template_mods
    ADD CONSTRAINT spec_template_mods_unique UNIQUE (spec_template_id, service_id, env,
                                                     host_name, domain_name, circuit_id, type);

-- create external events

DROP TABLE IF EXISTS external_events CASCADE;
CREATE TABLE external_events(
    id SERIAL PRIMARY KEY,
    link TEXT NOT NULL,
    start_ts TIMESTAMPTZ NOT NULL,
    deadline_ts TIMESTAMPTZ,
    event_type TEXT NOT NULL,
    event_data JSONB NOT NULL,
    revision SERIAL,
    finish_ts TIMESTAMPTZ,
    is_finished BOOLEAN NOT NULL DEFAULT FALSE
);
DROP INDEX IF EXISTS external_events_in_progress_by_link CASCADE;
CREATE UNIQUE INDEX external_events_in_progress_by_link
    ON external_events(link)
    WHERE (is_finished = FALSE);

DROP TYPE IF EXISTS external_event_v1 CASCADE;
CREATE TYPE external_event_v1 AS(
    id INTEGER,
    link TEXT,
    start_ts TIMESTAMPTZ,
    deadline_ts TIMESTAMPTZ,
    event_type TEXT,
    event_data JSONB,
    revision INTEGER,
    finish_ts TIMESTAMPTZ
);

DROP INDEX IF EXISTS external_event_is_finished_index CASCADE;
CREATE INDEX external_event_is_finished_index
    ON external_events(is_finished)
    WHERE is_finished = false;

-- add apply_when to mods

ALTER TABLE spec_template_mods
    ADD COLUMN apply_when TEXT NOT NULL DEFAULT 'always';

ALTER TABLE spec_template_mods
    DROP CONSTRAINT IF EXISTS spec_template_mods_unique;
ALTER TABLE spec_template_mods
    ADD CONSTRAINT spec_template_mods_unique UNIQUE (spec_template_id, service_id, env,
                                                     host_name, domain_name, circuit_id, type, apply_when);

-- create test cases

DROP TABLE IF EXISTS test_cases CASCADE;
CREATE TABLE test_cases(
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL DEFAULT '',
    test_data_id INTEGER NOT NULL,
    schema_id TEXT NOT NULL,
    out_point_id TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    check_type TEXT NOT NULL,
    check_params JSONB NOT NULL DEFAULT '{}',
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE
);

DROP INDEX IF EXISTS test_cases_schema_id_index CASCADE;
CREATE INDEX test_cases_schema_id_index
    ON test_cases(schema_id);

-- Add description to test_data

ALTER TABLE test_data
    ADD COLUMN description TEXT NOT NULL DEFAULT '';

UPDATE test_data
SET description = concat(
        'Test data for circuit ',
        meta::json->'circuit_id');

-- Set default value to out_point_id

ALTER TABLE test_data
    ALTER out_point_id SET DEFAULT '';

-- Add type to circuit_schemas

ALTER TABLE circuit_schemas
    ADD COLUMN type TEXT NOT NULL DEFAULT 'schema';

UPDATE circuit_schemas
SET type = circuit_schema::json->'type';

COMMIT TRANSACTION;

-- Add multi template in circuit_id_like in digests

BEGIN TRANSACTION;

ALTER TABLE digests
    ALTER COLUMN circuit_id_like TYPE TEXT[] USING ARRAY[circuit_id_like]::TEXT[],
    ALTER COLUMN circuit_id_like SET DEFAULT '{}';

-- add tvm_name to services table

ALTER TABLE services
    ADD COLUMN tvm_name TEXT;

DROP TYPE IF EXISTS service_v7 CASCADE;
CREATE TYPE service_v7 AS(
                             id INTEGER,
                             name TEXT,
                             cluster_type TEXT,
                             updated TIMESTAMPTZ,
                             deleted BOOLEAN,
                             project_id INTEGER,
                             project_name TEXT,
                             maintainers TEXT[],
                             chief TEXT,
                             service_link TEXT,
                             tvm_name TEXT
                         );

COMMIT TRANSACTION;

-- Add branch_domain_primary_key_v1 type

BEGIN TRANSACTION;

DROP TYPE IF EXISTS branch_domain_primary_key_v1 CASCADE;
CREATE TYPE branch_domain_primary_key_v1 AS(
                                               branch_id INTEGER,
                                               solomon_object TEXT
                                           );


COMMIT TRANSACTION;

-- Add branch_domain_primary_key_v1 type

BEGIN TRANSACTION;

DROP TYPE IF EXISTS branch_host_v2 CASCADE;
CREATE TYPE branch_host_v2 AS(
                                 host_name TEXT,
                                 branch_id INTEGER,
                                 datacenter TEXT
                             );

ALTER TABLE branch_hosts
    ADD COLUMN datacenter TEXT NOT NULL DEFAULT '';

COMMIT TRANSACTION;

-- Remove chief from services table

BEGIN TRANSACTION;

ALTER TABLE services
    DROP COLUMN chief;

DROP TYPE IF EXISTS service_v8 CASCADE;
CREATE TYPE service_v8 AS(
                             id INTEGER,
                             name TEXT,
                             cluster_type TEXT,
                             updated TIMESTAMPTZ,
                             deleted BOOLEAN,
                             project_id INTEGER,
                             project_name TEXT,
                             maintainers TEXT[],
                             service_link TEXT,
                             tvm_name TEXT
                         );

COMMIT TRANSACTION;

-- Remove hosts table (obsolete)

BEGIN TRANSACTION;

DROP TABLE IF EXISTS hosts CASCADE;
DROP TYPE IF EXISTS host_v1 CASCADE;

COMMIT TRANSACTION;

-- Add TVM rules table

BEGIN TRANSACTION;

DROP TYPE IF EXISTS TVM_ENVIRONMENT CASCADE;
CREATE TYPE TVM_ENVIRONMENT AS ENUM (
    'production', 'testing', 'unstable'
);

DROP TYPE IF EXISTS tvm_rule_v1 CASCADE;
CREATE TYPE tvm_rule_v1 AS(
    rule_id INTEGER,
    src_tvm_id INTEGER,
    src_tvm_name TEXT,
    dst_tvm_id INTEGER,
    dst_tvm_name TEXT,
    env TVM_ENVIRONMENT,
    updated TIMESTAMPTZ,
    deleted BOOLEAN
);

DROP TABLE IF EXISTS tvm_rules CASCADE;
CREATE TABLE tvm_rules(
    rule_id INTEGER PRIMARY KEY,
    src_tvm_id INTEGER NOT NULL,
    src_tvm_name TEXT NOT NULL,
    dst_tvm_id INTEGER NOT NULL,
    dst_tvm_name TEXT NOT NULL,
    env TVM_ENVIRONMENT NOT NULL,
    updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

COMMIT TRANSACTION;

-- Add DB dependencies table

BEGIN TRANSACTION;

DROP TYPE IF EXISTS db_dependency_v1 CASCADE;
CREATE TYPE db_dependency_v1 AS(
    service_id INTEGER,
    db_id INTEGER,
    updated TIMESTAMPTZ,
    deleted BOOLEAN
);

DROP TYPE IF EXISTS db_dependency_primary_key_v1 CASCADE;
CREATE TYPE db_dependency_primary_key_v1 AS(
    service_id INTEGER,
    db_id INTEGER
);

DROP TABLE IF EXISTS db_dependencies CASCADE;
CREATE TABLE db_dependencies(
    service_id INTEGER NOT NULL,
    db_id INTEGER NOT NULL,
    updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (service_id, db_id)
);

COMMIT TRANSACTION;

-- Custom metrics table

BEGIN TRANSACTION;

DROP TABLE IF EXISTS custom_metrics CASCADE;
CREATE TABLE custom_metrics(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    service_id INTEGER,
    schema_id TEXT NOT NULL,
    flows JSONB NOT NULL,
    alert_details TEXT,
    revision SERIAL,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

DROP INDEX IF EXISTS custom_metrics_service_id_index CASCADE;
CREATE INDEX custom_metrics_service_id_index
    ON custom_metrics(service_id);

COMMIT TRANSACTION;

-- Add column custom to table circuit_schemas

BEGIN TRANSACTION;

ALTER TABLE circuit_schemas
    ADD COLUMN custom BOOLEAN NOT NULL DEFAULT FALSE;

COMMIT TRANSACTION;

-- Add column expiration_point to table spec_template_mods

BEGIN TRANSACTION;

ALTER TABLE spec_template_mods
    ADD COLUMN expiration_point TIMESTAMPTZ DEFAULT NULL;

COMMIT TRANSACTION;

-- Add column expired to table spec_template_mods

BEGIN TRANSACTION;

ALTER TABLE spec_template_mods
    ADD COLUMN expired BOOLEAN NOT NULL DEFAULT FALSE;

COMMIT TRANSACTION;

-- Add external_events.revision index

BEGIN TRANSACTION;

DROP INDEX IF EXISTS external_events_revision_index CASCADE;
CREATE INDEX external_events_revision_index
    ON external_events(revision);

COMMIT TRANSACTION;

-- Add table custom_checks and copy data from custom_metrics

BEGIN TRANSACTION;

DROP TABLE IF EXISTS custom_checks CASCADE;
CREATE TABLE custom_checks(
                              id BIGSERIAL PRIMARY KEY,
                              name TEXT NOT NULL,
                              description TEXT,
                              service_id INTEGER,
                              schema_id TEXT NOT NULL,
                              flows JSONB NOT NULL,
                              alert_details TEXT,
                              revision BIGSERIAL,
                              deleted BOOLEAN NOT NULL DEFAULT FALSE
);

DROP INDEX IF EXISTS custom_checks_service_id_index CASCADE;
CREATE INDEX custom_checks_service_id_index
    ON custom_checks(service_id);

INSERT INTO custom_checks
(name, description, service_id, schema_id, flows, alert_details, deleted)
SELECT
    name, description, service_id, schema_id, flows, alert_details, deleted
FROM custom_metrics;

COMMIT TRANSACTION;

-- Remove table custom_metrics

BEGIN TRANSACTION;

DROP INDEX IF EXISTS custom_metrics_service_id_index CASCADE;
DROP TABLE IF EXISTS custom_metrics CASCADE;

COMMIT TRANSACTION;

-- Create uptime_cache table

BEGIN TRANSACTION;

DROP TABLE IF EXISTS services_uptime CASCADE;
CREATE TABLE services_uptime(
    service_id INTEGER CONSTRAINT services_uptime_pk PRIMARY KEY,
    uptime_1d DOUBLE PRECISION NOT NULL,
    uptime_7d DOUBLE PRECISION NOT NULL,
    uptime_30d DOUBLE PRECISION NOT NULL,
    updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

DROP TYPE IF EXISTS service_uptime_v1 CASCADE;
CREATE TYPE service_uptime_v1 AS (
    service_id INTEGER,
    uptime_1d DOUBLE PRECISION,
    uptime_7d DOUBLE PRECISION,
    uptime_30d DOUBLE PRECISION,
    updated TIMESTAMPTZ
);

COMMIT TRANSACTION;

-- Add unique constraint on custom_check table

DROP INDEX IF EXISTS custom_check_unique_name_per_service CASCADE;
CREATE UNIQUE INDEX custom_check_unique_name_per_service
    ON custom_checks(name, coalesce(service_id, 0))
    WHERE NOT deleted;

-- Add columns recipients and updated to custom_check table

ALTER TABLE custom_checks
    ADD COLUMN recipients TEXT[] NOT NULL DEFAULT '{}',
    ADD COLUMN updated TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- Create table for juggler check states

DROP TYPE IF EXISTS juggler_alert_status CASCADE;
CREATE TYPE juggler_alert_status AS ENUM (
    'OK', 'WARN', 'CRIT'
);

DROP TABLE IF EXISTS juggler_check_states CASCADE;
CREATE TABLE juggler_check_states(
    service TEXT NOT NULL,
    host TEXT NOT NULL,
    status juggler_alert_status NOT NULL,
    description TEXT,
    meta JSONB NOT NULL DEFAULT '{}',
    updated TIMESTAMP NOT NULL,
    changed TIMESTAMP NOT NULL,
    PRIMARY KEY (service, host)
);

DROP INDEX IF EXISTS juggler_check_states_updated_index CASCADE;
CREATE INDEX juggler_check_states_updated_index
    ON juggler_check_states(updated);

DROP TYPE IF EXISTS juggler_check_state CASCADE;
CREATE TYPE juggler_check_state AS (
    service TEXT,
    host TEXT,
    status juggler_alert_status,
    description TEXT,
    meta JSONB,
    updated TIMESTAMP,
    changed TIMESTAMP
);

-- Create type for primary key on juggler_check_states

DROP TYPE IF EXISTS juggler_check_state_id CASCADE;
CREATE TYPE juggler_check_state_id AS (
    service TEXT,
    host TEXT
);

-- add 'expired' value for draft_approve_status

ALTER TYPE draft_approve_status ADD VALUE 'expired';

-- Add ticket column to custom_checks table

ALTER TABLE custom_checks
    ADD COLUMN ticket TEXT NOT NULL DEFAULT '';

-- Add column deleted to juggler_check_states

ALTER TABLE juggler_check_states
    ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT FALSE;

DROP TYPE IF EXISTS juggler_check_state_v2 CASCADE;
CREATE TYPE juggler_check_state_v2 AS (
    service TEXT,
    host TEXT,
    status juggler_alert_status,
    description TEXT,
    meta JSONB,
    updated TIMESTAMP,
    changed TIMESTAMP,
    deleted BOOLEAN
);

-- Add column ema to juggler_check_states

ALTER TABLE juggler_check_states
    ADD COLUMN last_update_period INTERVAL DEFAULT NULL,
    ADD COLUMN update_period_ema INTERVAL DEFAULT NULL;

DROP TYPE IF EXISTS juggler_check_state_v3 CASCADE;
CREATE TYPE juggler_check_state_v3 AS (
    service TEXT,
    host TEXT,
    status juggler_alert_status,
    description TEXT,
    meta JSONB,
    updated TIMESTAMP,
    changed TIMESTAMP,
    deleted BOOLEAN,
    last_update_period INTERVAL,
    update_period_ema INTERVAL
);

-- Add group_by_labels column to custom_checks table

BEGIN TRANSACTION;

ALTER TABLE custom_checks
    ADD COLUMN group_by_label TEXT,
    ADD COLUMN group_by_label_vals TEXT[];

COMMIT TRANSACTION;


BEGIN TRANSACTION ;

ALTER TABLE services
    ADD COLUMN service_tier TEXT default null;

DROP TYPE IF EXISTS service_v9 CASCADE;
CREATE TYPE service_v9 AS(
                             id INTEGER,
                             name TEXT,
                             cluster_type TEXT,
                             updated TIMESTAMPTZ,
                             deleted BOOLEAN,
                             project_id INTEGER,
                             project_name TEXT,
                             maintainers TEXT[],
                             service_link TEXT,
                             tvm_name TEXT,
                             service_tier TEXT
                         );

COMMIT TRANSACTION;
