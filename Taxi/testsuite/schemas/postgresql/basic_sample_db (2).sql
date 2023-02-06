CREATE SCHEMA basic_sample_db;

/* For types other than ENUM use versioning! */
CREATE TYPE basic_sample_db.action_t AS ENUM (
    'standing', 'walking', 'running'
);

CREATE TABLE basic_sample_db.main_table (
    id                 BIGSERIAL                NOT NULL PRIMARY KEY,
    name               TEXT                     NOT NULL UNIQUE,
    action             basic_sample_db.action_t NOT NULL,
    previous_action    basic_sample_db.action_t NOT NULL,
    updated_at         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
