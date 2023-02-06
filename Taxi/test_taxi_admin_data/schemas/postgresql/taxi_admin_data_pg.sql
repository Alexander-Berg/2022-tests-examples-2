DROP SCHEMA IF EXISTS data CASCADE;
CREATE SCHEMA data;

CREATE TABLE data.shared_data (
    key text PRIMARY KEY,
    value text NOT NULL
);

CREATE TABLE data.private_data (
    user_login text NOT NULL,
    key text  NOT NULL,
    value text NOT NULL,
    PRIMARY KEY(user_login, key)
);
