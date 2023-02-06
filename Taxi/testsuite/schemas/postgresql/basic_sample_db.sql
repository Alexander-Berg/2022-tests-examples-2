CREATE SCHEMA basic_sample_db;

CREATE TYPE basic_sample_db.key_foo_enum_type AS ENUM (
    'key_pg',
    'key_yt'
);

CREATE TABLE basic_sample_db.main_table (
    key_foo            TEXT                     NOT NULL,
    key_bar            BIGINT                   NOT NULL,
    value              TEXT                     NOT NULL,
    updated_ts         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    key_foo_enum       basic_sample_db.key_foo_enum_type,

    PRIMARY KEY (key_foo, key_bar)
);

CREATE TABLE basic_sample_db.second_table (
    key_foo            TEXT                     NOT NULL,
    key_bar            BIGINT                   NOT NULL,
    second_value       TEXT                     NOT NULL,

    PRIMARY KEY (key_foo, key_bar)
);
