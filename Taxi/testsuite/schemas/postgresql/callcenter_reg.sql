DROP SCHEMA IF EXISTS callcenter_reg CASCADE;

CREATE SCHEMA callcenter_reg;

CREATE TABLE callcenter_reg.agent
(
    sip_username VARCHAR NOT NULL
                    CONSTRAINT agent_pkey
                    UNIQUE,
    reg_node VARCHAR,
    reg_status VARCHAR,
    user_socket VARCHAR,
    supervisor VARCHAR
                CONSTRAINT agent_supervisor_key
                UNIQUE,
    yandex_uid VARCHAR NOT NULL
                CONSTRAINT agent_yandex_uid_key
                    PRIMARY KEY,
    reg_status_updated_at TIMESTAMPTZ NOT NULL
                            DEFAULT NOW()
);

CREATE TYPE callcenter_reg.agent_info AS (
    yandex_uid VARCHAR,
    sip_username VARCHAR
);

CREATE TABLE IF NOT EXISTS callcenter_reg.sip_user_status (
    sip_username VARCHAR PRIMARY KEY,
    status  VARCHAR NOT NULL,
    sub_status VARCHAR,
    project VARCHAR NOT NULL,
    pg_created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pg_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX sip_user_status_created_at_idx ON callcenter_reg.sip_user_status(pg_created_at);
CREATE INDEX sip_user_status_project_idx ON callcenter_reg.sip_user_status(project);

CREATE SEQUENCE callcenter_reg.sip_user_status_update_seq;
ALTER TABLE callcenter_reg.sip_user_status ADD COLUMN update_seq BIGINT NOT NULL DEFAULT nextval('callcenter_reg.sip_user_status_update_seq');
ALTER SEQUENCE callcenter_reg.sip_user_status_update_seq OWNED BY callcenter_reg.sip_user_status.update_seq;

CREATE OR REPLACE FUNCTION trigger_inc_sip_user_status_update_seq()
    RETURNS TRIGGER AS $$
BEGIN
    NEW.update_seq = nextval('callcenter_reg.sip_user_status_update_seq');
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER global_inc_sip_user_status_update_seq
    BEFORE UPDATE ON callcenter_reg.sip_user_status
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_inc_sip_user_status_update_seq();

CREATE UNIQUE INDEX IF NOT EXISTS sip_user_status_update_seq_uniqueness ON callcenter_reg.sip_user_status (update_seq);
ALTER TABLE callcenter_reg.sip_user_status ADD CONSTRAINT sip_user_status_update_seq_uniqueness UNIQUE USING INDEX sip_user_status_update_seq_uniqueness;
