#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE dbapprovals;
\connect dbapprovals

DROP SCHEMA IF EXISTS approvals_schema CASCADE;
CREATE SCHEMA approvals_schema;

DROP TABLE IF EXISTS approvals_schema.drafts CASCADE;
CREATE TABLE approvals_schema.drafts
(
    id            bigserial PRIMARY KEY,
    created_by    text                        NOT NULL,
    comments      jsonb,
    created       timestamp without time zone NOT NULL,
    updated       timestamp without time zone NOT NULL,
    apply_time    timestamp without time zone,
    description   text,
    approvals     jsonb,
    status        text                        NOT NULL,
    version       smallint,
    request_id    text                        NOT NULL UNIQUE,
    run_manually  boolean,
    service_name  text                        NOT NULL,
    api_path      text                        NOT NULL,
    data          jsonb,
    change_doc_id text                        NOT NULL UNIQUE,
    rejected_by   text
);
CREATE INDEX service_name_key ON approvals_schema.drafts (service_name);
CREATE INDEX api_path_key ON approvals_schema.drafts (api_path);

CREATE FUNCTION approvals_schema.update_version_and_updated() RETURNS TRIGGER
AS
'
BEGIN
    NEW.updated := CURRENT_TIMESTAMP AT TIME ZONE ''UTC'';
    IF TG_OP = ''UPDATE'' THEN
        NEW.version := OLD.version + 1;
    END IF;

    RETURN NEW;
END;
' LANGUAGE plpgsql;

CREATE TRIGGER update_version_and_updated_tr
    BEFORE INSERT OR UPDATE
    ON approvals_schema.drafts
    FOR EACH ROW
EXECUTE PROCEDURE approvals_schema.update_version_and_updated();

/* adding field "mode" to different types of approvals */
ALTER TABLE approvals_schema.drafts
    ADD mode text NOT NULL DEFAULT 'push';

/* adding field "summon_mode" to specify mode of summoning approvals */
ALTER TABLE approvals_schema.drafts
    ADD summon_mode text NOT NULL
        DEFAULT 'no_summon';

/* adding field "ticket" */
ALTER TABLE approvals_schema.drafts
    ADD ticket text;

/* changing unique field into unique index with condition */
CREATE UNIQUE INDEX change_doc_id_key ON approvals_schema.drafts (change_doc_id)
    WHERE status = 'need_approval' OR status = 'approved'
        OR status = 'applying';
ALTER TABLE approvals_schema.drafts
    DROP CONSTRAINT drafts_change_doc_id_key;

/* adding field "tickets" */
ALTER TABLE approvals_schema.drafts
    ADD tickets jsonb DEFAULT '[]'::jsonb;

/* migrate ticket to tickets. empty array if ticket is null */
UPDATE approvals_schema.drafts
SET tickets = tickets || coalesce(to_jsonb(ticket), '[]'::jsonb)
WHERE NOT tickets ? ticket;

/* dropping field "ticket" */
ALTER TABLE approvals_schema.drafts
    DROP COLUMN ticket;

CREATE TABLE approvals_schema.summons
(
    id           bigserial PRIMARY KEY,
    draft_id     integer                     NOT NULL
        REFERENCES approvals_schema.drafts (id) ON DELETE CASCADE,
    yandex_login text                        NOT NULL,
    summoned     timestamp without time zone NOT NULL
);

CREATE UNIQUE INDEX summons_draft_id_yandex_login
    ON approvals_schema.summons (draft_id, yandex_login);

CREATE INDEX summons_yandex_login
    ON approvals_schema.summons (yandex_login);

/* dropping field "summon_mode" */
ALTER TABLE approvals_schema.drafts
    DROP COLUMN summon_mode;

/* adding field "summary" */
ALTER TABLE approvals_schema.drafts
    ADD summary jsonb not null
        DEFAULT '{}'::jsonb;

CREATE TABLE approvals_schema.lock_ids
(
    id       bigserial PRIMARY KEY,
    draft_id integer NOT NULL
        REFERENCES approvals_schema.drafts (id) ON DELETE CASCADE,
    lock_id  text    NOT NULL
);

CREATE UNIQUE INDEX lock_ids_lock_id_unique
    ON approvals_schema.lock_ids (lock_id);

CREATE INDEX lock_ids_draft_id ON approvals_schema.lock_ids (draft_id);

ALTER TABLE approvals_schema.drafts
    ADD deferred_apply
        timestamp without time zone;

ALTER TABLE approvals_schema.drafts
    ADD errors jsonb DEFAULT '[]'::jsonb;

ALTER TABLE approvals_schema.drafts
    ADD headers jsonb DEFAULT '{}'::jsonb;
ALTER TABLE approvals_schema.drafts
    ADD query_params jsonb DEFAULT '{}'::jsonb;

ALTER TABLE approvals_schema.drafts
    ADD is_multidraft boolean NOT NULL
        DEFAULT false;

ALTER TABLE approvals_schema.drafts
    ADD multidraft_id integer
        REFERENCES approvals_schema.drafts (id) ON DELETE RESTRICT
        DEFAULT null::integer;

CREATE INDEX drafts_is_multidraft
    ON approvals_schema.drafts (is_multidraft);

CREATE INDEX drafts_multidraft_id
    ON approvals_schema.drafts (multidraft_id);

CREATE TABLE approvals_schema.responsibles
(
    id           bigserial PRIMARY KEY,
    draft_id     integer NOT NULL
        REFERENCES approvals_schema.drafts (id) ON DELETE CASCADE,
    yandex_login text    NOT NULL
);

CREATE UNIQUE INDEX responsibles_draft_id_yandex_login_unique
    ON approvals_schema.responsibles (draft_id, yandex_login);

ALTER TABLE approvals_schema.drafts
    ADD reminded timestamp without time zone
        DEFAULT null::timestamp;

CREATE INDEX drafts_deferred_apply_reminded
    ON approvals_schema.drafts (deferred_apply, reminded);


CREATE TYPE approvals_schema.error_type_t AS ENUM (
  'other',
  'timeout',
  'bad_response',
  'internal_server_error',
  'exception'
);

CREATE TABLE approvals_schema.process_errors (
    id bigserial PRIMARY KEY,
    draft_id bigint NOT NULL
        REFERENCES approvals_schema.drafts(id) ON DELETE CASCADE,
    response_body text,
    response_status integer,
    response_headers jsonb,
    error_type approvals_schema.error_type_t NOT NULL,
    details text,
    error_processed boolean NOT NULL DEFAULT false
);

CREATE UNIQUE INDEX process_errors_draft_id_unique
    ON approvals_schema.process_errors (draft_id);

CREATE INDEX process_errors_error_processed
    ON approvals_schema.process_errors (error_processed)
    WHERE error_processed is false;

ALTER TABLE approvals_schema.drafts ADD start_apply_time timestamp without time zone
DEFAULT null::timestamp;
ALTER TABLE approvals_schema.drafts ADD finish_apply_time timestamp without time zone
DEFAULT null::timestamp;

ALTER TABLE approvals_schema.drafts ADD date_expired timestamp without time zone
DEFAULT null::timestamp;

CREATE INDEX drafts_status_apply_time
    ON approvals_schema.drafts (status, apply_time);

ALTER INDEX approvals_schema.change_doc_id_key RENAME TO change_doc_id_key_old;

CREATE UNIQUE INDEX CONCURRENTLY change_doc_id_key
ON approvals_schema.drafts(change_doc_id)
WHERE status IN ('waiting_check', 'need_approval', 'approved', 'applying');

DROP INDEX CONCURRENTLY approvals_schema.change_doc_id_key_old;

CREATE TYPE approvals_schema.scheme_type_e AS ENUM (
    'admin',
    'platform'
);

ALTER TABLE approvals_schema.drafts
    ADD COLUMN scheme_type approvals_schema.scheme_type_e DEFAULT NULL;

CREATE INDEX CONCURRENTLY drafts_scheme_type
    ON approvals_schema.drafts (scheme_type);

CREATE TABLE approvals_schema.fields (
    id bigserial primary key,
    service_name text not null,
    api_path text not null,
    path text not null
);

CREATE UNIQUE INDEX fields_service_name_api_path_path_index_unique
    ON approvals_schema.fields (service_name, api_path, path);

CREATE TYPE approvals_schema.scheme_field_values_value_type AS enum (
    'integer',
    'string'
);

CREATE TABLE approvals_schema.field_values(
    id bigserial primary key,
    field_id bigint not null references approvals_schema.fields(id) ON DELETE CASCADE,
    draft_id bigint not null
        references approvals_schema.drafts(id) ON DELETE CASCADE,
    value text,
    value_type approvals_schema.scheme_field_values_value_type
);

CREATE INDEX field_values_draft_id
    ON approvals_schema.field_values (draft_id);

CREATE INDEX field_values_field_id_value_index
    ON approvals_schema.field_values (field_id, value);

CREATE FUNCTION pg_temp.create_draft(
    created_by text, data jsonb, description text, change_doc_id text,
    request_id text, run_manually boolean, service_name text, api_path text,
    comments jsonb, created timestamp, approvals jsonb,
    status text, version smallint, mode text, tickets jsonb, summary jsonb,
    deferred_apply timestamp, errors jsonb, headers jsonb, query_params jsonb,
    is_multidraft bool, date_expired timestamp,
    scheme_type approvals_schema.scheme_type_e
)
    RETURNS bigint AS
'
DECLARE
    new_draft_id bigint;
BEGIN
    INSERT INTO
        approvals_schema.drafts (
            created_by, comments, created, description, approvals,
            status, version, request_id, run_manually, service_name,
            api_path, data, change_doc_id, mode, tickets, summary,
            deferred_apply, errors, headers, query_params, is_multidraft,
            date_expired, scheme_type
        )
        VALUES (
            created_by, comments, created, description, approvals,
            status, version, request_id, run_manually, service_name,
            api_path, data, change_doc_id, mode, tickets, summary,
            deferred_apply, errors, headers, query_params, is_multidraft,
            date_expired, scheme_type
        ) RETURNING id INTO new_draft_id;
    RETURN new_draft_id;
END
'
LANGUAGE plpgsql;


EOSQL
