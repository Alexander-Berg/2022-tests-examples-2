START TRANSACTION;

CREATE SCHEMA form_builder;

CREATE TYPE form_builder.translatable AS (
    tanker_key TEXT,
    static_value TEXT
);

CREATE TYPE form_builder.choice AS (
    value JSONB,
    title form_builder.translatable
);

CREATE TABLE form_builder.field_templates (
    id BIGSERIAL PRIMARY KEY,
    name TEXT,
    value_type TEXT,
    is_array BOOLEAN NOT NULL,
    personal_data_type TEXT,
    has_choices BOOLEAN NOT NULL,
    default_label form_builder.translatable,
    default_placeholder form_builder.translatable,
    default_hint form_builder.translatable,
    default_choices form_builder.choice[],
    tags TEXT[] NOT NULL,
    regex_pattern TEXT,
    -- builder fields below
    author TEXT NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    updated TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE TABLE form_builder.forms (
    id BIGSERIAL PRIMARY KEY,
    guide_line TEXT,
    code TEXT NOT NULL UNIQUE,
    title form_builder.translatable,
    description form_builder.translatable,
    conditions JSONB NOT NULL,
    default_locale TEXT NOT NULL,
    supported_locales TEXT[] NOT NULL,
    -- builder fields below
    author TEXT NOT NULL,
    access_group TEXT,
    created TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    updated TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE TYPE form_builder.submit_header AS (
    name TEXT,
    value TEXT
);

CREATE TYPE form_builder.submit_options_host_check_state AS ENUM (
    'SUCCESS',
    'FAILED'
);


CREATE TABLE form_builder.submit_options (
    id BIGSERIAL PRIMARY KEY,
    form_code TEXT REFERENCES form_builder.forms(code) ON DELETE CASCADE NOT NULL,
    method TEXT NOT NULL,
    url TEXT NOT NULL,
    headers form_builder.submit_header[] NOT NULL,
    tvm_service_id TEXT,
    body_template TEXT NOT NULL,
    -- host check status
    host TEXT,
    port SMALLINT,
    host_check_state form_builder.submit_options_host_check_state,
    host_check_fail_reason TEXT,
    last_host_check_time TIMESTAMPTZ
);

CREATE TABLE form_builder.stages (
    id BIGSERIAL PRIMARY KEY,
    form_code TEXT REFERENCES form_builder.forms(code) ON DELETE CASCADE,
    title form_builder.translatable,
    description form_builder.translatable
);

CREATE TABLE form_builder.fields (
    id BIGSERIAL PRIMARY KEY,
    stage_id BIGSERIAL REFERENCES form_builder.stages(id) ON DELETE CASCADE,
    code TEXT,
    template_id BIGSERIAL REFERENCES form_builder.field_templates(id) ON DELETE RESTRICT,
    visible BOOLEAN NOT NULL,
    obligatory BOOLEAN,
    default_value JSONB,
    label form_builder.translatable,
    placeholder form_builder.translatable,
    hint form_builder.translatable,
    choices form_builder.choice[],
    obligation_condition TEXT,
    visibility_condition TEXT
);

CREATE TABLE form_builder.responses (
    id BIGSERIAL PRIMARY KEY,
    form_code TEXT REFERENCES form_builder.forms(code) ON DELETE RESTRICT,
    created TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE TABLE form_builder.response_values (
    id BIGSERIAL PRIMARY KEY,
    response_id BIGSERIAL REFERENCES form_builder.responses(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value JSONB,
    -- template fields values below (state at the creation time of the row)
    value_type TEXT,
    is_array BOOLEAN NOT NULL,
    personal_data_type TEXT
);

CREATE TYPE form_builder.submit_status AS ENUM (
    'PENDING',
    'SUBMITTED',
    'FAILED'
);

CREATE TABLE form_builder.request_queue (
    response_id BIGSERIAL REFERENCES form_builder.responses(id) ON DELETE CASCADE,
    status form_builder.submit_status NOT NULL,
    fail_count INTEGER NOT NULL DEFAULT 0,
    created TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    updated TIMESTAMPTZ NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    -- submit options values below (state at the creation time of the row)
    method TEXT NOT NULL,
    url TEXT NOT NULL,
    headers form_builder.submit_header[] NOT NULL,
    tvm_service_id TEXT,
    body_template TEXT NOT NULL
);

CREATE FUNCTION set_updated() RETURNS trigger AS $set_updated$
    BEGIN
        NEW.updated = (NOW() AT TIME ZONE 'UTC');
        RETURN NEW;
    END;
$set_updated$ LANGUAGE plpgsql;

CREATE TRIGGER request_queue_set_updated BEFORE UPDATE OR INSERT ON form_builder.request_queue
FOR EACH ROW EXECUTE PROCEDURE set_updated();

COMMIT;
