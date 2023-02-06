CREATE SCHEMA se;

CREATE TABLE se.nalogru_phone_bindings
(
    phone_pd_id                TEXT NOT NULL PRIMARY KEY,
    status                     TEXT NOT NULL,
    inn_pd_id                  TEXT UNIQUE,
    bind_request_id            TEXT,
    bind_requested_at          TIMESTAMP WITH TIME ZONE,
    created_at                 TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at                 TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    increment                  BIGSERIAL,
    exceeded_legal_income_year SMALLINT,
    business_unit              TEXT NOT NULL DEFAULT 'taxi'
);

CREATE INDEX se_nalogru_phone_bindings_replication_idx
    ON se.nalogru_phone_bindings (updated_at);

CREATE INDEX nalogru_phone_bindings_increment_idx
    ON se.nalogru_phone_bindings (increment);

CREATE TABLE se.finished_profiles
(
    park_id               TEXT NOT NULL,
    contractor_profile_id TEXT NOT NULL,
    phone_pd_id           TEXT NOT NULL REFERENCES se.nalogru_phone_bindings,
    inn_pd_id             TEXT NOT NULL,
    do_send_receipts      BOOLEAN DEFAULT TRUE  NOT NULL,
    is_own_park           BOOLEAN DEFAULT TRUE  NOT NULL,
    created_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    increment             BIGSERIAL,
    business_unit         TEXT NOT NULL DEFAULT 'taxi',
    PRIMARY KEY (park_id, contractor_profile_id)
);

CREATE INDEX se_finished_profiles_replication_idx
    ON se.finished_profiles (updated_at);

CREATE INDEX finished_profiles_phone_pd_id_idx
    ON se.finished_profiles (phone_pd_id);

CREATE INDEX finished_profiles_increment_idx
    ON se.finished_profiles (increment);

CREATE TABLE se.ownpark_profile_forms_common
(
    phone_pd_id                   TEXT NOT NULL PRIMARY KEY,
    state                         TEXT NOT NULL,
    address                       TEXT,
    apartment_number              TEXT,
    postal_code                   TEXT,
    agreements                    jsonb,
    inn_pd_id                     TEXT,
    residency_state               TEXT,
    salesforce_account_id         TEXT,
    salesforce_requisites_case_id TEXT,
    initial_park_id               TEXT,
    initial_contractor_id         TEXT,
    created_park_id               TEXT,
    created_contractor_id         TEXT,
    increment                     BIGSERIAL,
    created_at                    TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at                    TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    salesforce_opportunity_id     TEXT,
    external_id                   TEXT NOT NULL UNIQUE
);

CREATE INDEX ownpark_profile_forms_common_updated_at_idx
    ON se.ownpark_profile_forms_common (updated_at);

CREATE INDEX ownpark_profile_forms_common_increment_idx
    ON se.ownpark_profile_forms_common (increment);

CREATE TABLE se.ownpark_profile_forms_contractor
(
    initial_park_id       TEXT NOT NULL,
    initial_contractor_id TEXT NOT NULL,
    phone_pd_id           TEXT,
    is_phone_verified     BOOLEAN DEFAULT TRUE NOT NULL,
    track_id              TEXT,
    last_step             TEXT NOT NULL DEFAULT 'intro',
    increment             BIGSERIAL,
    created_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    profession            TEXT NOT NULL DEFAULT 'taxi-driver',
    PRIMARY KEY (initial_park_id, initial_contractor_id)
);

CREATE INDEX ownpark_profile_forms_contractor_updated_at_idx
    ON se.ownpark_profile_forms_contractor (updated_at);

CREATE INDEX ownpark_profile_forms_contractor_increment_idx
    ON se.ownpark_profile_forms_contractor (increment);

CREATE TABLE se.finished_ownpark_profile_metadata
(
    created_park_id               TEXT NOT NULL,
    created_contractor_id         TEXT NOT NULL,
    phone_pd_id                   TEXT NOT NULL,
    initial_park_id               TEXT NOT NULL,
    initial_contractor_id         TEXT NOT NULL,
    salesforce_account_id         TEXT,
    salesforce_requisites_case_id TEXT,
    increment                     BIGSERIAL,
    created_at                    TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at                    TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    external_id                   TEXT NOT NULL UNIQUE,
    PRIMARY KEY (created_park_id, created_contractor_id)
);

CREATE INDEX finished_ownpark_profile_metadata_updated_at_idx
    ON se.finished_ownpark_profile_metadata (updated_at);

CREATE INDEX finished_ownpark_profile_metadata_increment_idx
    ON se.finished_ownpark_profile_metadata (increment);

CREATE TABLE se.taxpayer_status_cache
(
    inn_pd_id                    TEXT PRIMARY KEY,
    first_name                   TEXT NOT NULL,
    second_name                  TEXT NOT NULL,
    registration_time            TIMESTAMPTZ NOT NULL,
    region_oktmo_code            TEXT NOT NULL,
    phone_pd_id                  TEXT NOT NULL,
    oksm_code                    TEXT,
    middle_name                  TEXT,
    unregistration_time          TIMESTAMPTZ,
    unregistration_reason        TEXT,
    activities                   jsonb,
    email                        TEXT,
    account_number               TEXT,
    update_time                  TEXT,
    registration_certificate_num TEXT,
    created_at                   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    increment                    BIGSERIAL NOT NULL
);

CREATE INDEX se_taxpayer_status_cache_replication_idx
    ON se.taxpayer_status_cache (updated_at);

CREATE INDEX taxpayer_status_cache_increment_idx
    ON se.taxpayer_status_cache (increment);

CREATE OR REPLACE FUNCTION touch_updated_record()
    RETURNS TRIGGER AS $$
BEGIN
    NEW.increment = NEXTVAL(TG_ARGV[0]);
    NEW.updated_at = NOW();
    RETURN NEW;
END
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER touch_updated_record
    BEFORE UPDATE
    ON se.nalogru_phone_bindings
    FOR EACH ROW
EXECUTE PROCEDURE touch_updated_record('se.nalogru_phone_bindings_increment_seq');

CREATE TRIGGER touch_updated_record
    BEFORE UPDATE
    ON se.finished_profiles
    FOR EACH ROW
EXECUTE PROCEDURE touch_updated_record('se.finished_profiles_increment_seq');

CREATE TRIGGER touch_updated_record
    BEFORE UPDATE
    ON se.ownpark_profile_forms_common
    FOR EACH ROW
EXECUTE PROCEDURE touch_updated_record('se.ownpark_profile_forms_common_increment_seq');

CREATE TRIGGER touch_updated_record
    BEFORE UPDATE
    ON se.ownpark_profile_forms_contractor
    FOR EACH ROW
EXECUTE PROCEDURE touch_updated_record('se.ownpark_profile_forms_contractor_increment_seq');

CREATE TRIGGER touch_updated_record
    BEFORE UPDATE
    ON se.finished_ownpark_profile_metadata
    FOR EACH ROW
EXECUTE PROCEDURE touch_updated_record('se.finished_ownpark_profile_metadata_increment_seq');

CREATE TRIGGER touch_updated_record
    BEFORE UPDATE
    ON se.taxpayer_status_cache
    FOR EACH ROW
EXECUTE PROCEDURE touch_updated_record('se.taxpayer_status_cache_increment_seq');

CREATE TYPE se.ownpark_common_form_t_v1 AS
(
    phone_pd_id                   TEXT,
    state                         TEXT,
    external_id                   TEXT,
    created_park_id               TEXT,
    created_contractor_id         TEXT,
    address                       TEXT,
    apartment_number              TEXT,
    postal_code                   TEXT,
    agreements                    jsonb,
    inn_pd_id                     TEXT,
    residency_state               TEXT,
    salesforce_account_id         TEXT,
    salesforce_requisites_case_id TEXT,
    initial_park_id               TEXT,
    initial_contractor_id         TEXT
);

CREATE TYPE se.ownpark_contractor_form_t_v1 AS
(
    initial_park_id       TEXT,
    initial_contractor_id TEXT,
    phone_pd_id           TEXT,
    is_phone_verified     BOOLEAN,
    track_id              TEXT,
    last_step             TEXT,
    profession            TEXT
);

CREATE TYPE se.nalogru_phone_binding_t_v1 AS
(
    phone_pd_id                TEXT,
    business_unit              TEXT,
    status                     TEXT,
    inn_pd_id                  TEXT,
    bind_request_id            TEXT,
    bind_requested_at          TIMESTAMP WITH TIME ZONE,
    exceeded_legal_income_year SMALLINT
);

CREATE TYPE se.finished_profile_t_v1 AS
(
    park_id               TEXT,
    contractor_profile_id TEXT,
    phone_pd_id           TEXT,
    business_unit         TEXT,
    inn_pd_id             TEXT,
    do_send_receipts      BOOLEAN,
    is_own_park           BOOLEAN
);

CREATE TYPE se.finished_ownpark_profile_metadata_t_v1 AS
(
    created_park_id               TEXT,
    created_contractor_id         TEXT,
    phone_pd_id                   TEXT,
    initial_park_id               TEXT,
    initial_contractor_id         TEXT,
    salesforce_account_id         TEXT,
    salesforce_requisites_case_id TEXT,
    external_id                   TEXT
);

CREATE TYPE se.taxpayer_status_t_v1 AS
(
    inn_pd_id TEXT,
    first_name TEXT,
    last_name TEXT,
    registration_time TIMESTAMPTZ,
    region_oktmo_code TEXT,
    phone_pd_id TEXT,
    oksm_code TEXT,
    middle_name TEXT,
    unregistration_time TIMESTAMPTZ,
    unregistration_reason TEXT,
    activities jsonb,
    email TEXT,
    account_number TEXT,
    update_time TEXT,
    registration_certificate_num TEXT
);
