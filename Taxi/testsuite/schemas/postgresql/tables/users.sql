CREATE TYPE access_control.user_provider_t AS ENUM ('yandex', 'restapp');

CREATE TYPE access_control.users_v1 AS (
    provider access_control.user_provider_t,
    provider_user_id TEXT,
    id INT
);

CREATE TABLE access_control.users
(
    id                 SERIAL      NOT NULL PRIMARY KEY,
    provider           TEXT        NOT NULL,
    provider_user_id   TEXT        NOT NULL,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX
    users_provider_provider_user_id
ON
    access_control.users (
        provider,
        provider_user_id
    );

CREATE TRIGGER groups_set_updated_at_timestamp
    BEFORE UPDATE ON access_control.users
    FOR EACH ROW
EXECUTE PROCEDURE trigger_set_updated_at_timestamp();
