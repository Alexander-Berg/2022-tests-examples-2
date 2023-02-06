CREATE TYPE access_control.http_method_t AS ENUM ('GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'PATCH');

CREATE TYPE access_control.restriction_t_v1 AS
(
    handler_path       TEXT,
    handler_method     access_control.http_method_t,
    restriction        JSONB
);

CREATE TABLE access_control.restrictions
(
    role_id            INTEGER     NOT NULL REFERENCES access_control.roles (id) ON DELETE CASCADE,
    handler_path       TEXT        NOT NULL,
    handler_method     access_control.http_method_t NOT NULL,
    restriction        JSONB       NOT NULL,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT         role_handler_path PRIMARY KEY (role_id, handler_path, handler_method)
);

CREATE TRIGGER restrictions_set_updated_at_timestamp
    BEFORE UPDATE ON access_control.restrictions
    FOR EACH ROW
EXECUTE PROCEDURE trigger_set_updated_at_timestamp();
