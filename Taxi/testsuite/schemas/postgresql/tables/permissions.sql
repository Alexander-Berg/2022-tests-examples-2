CREATE TABLE access_control.permissions
(
    id                 SERIAL      NOT NULL PRIMARY KEY,
    system_id          INTEGER     NOT NULL REFERENCES access_control.system (id) ON DELETE CASCADE,
    name               TEXT        NOT NULL,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX
    permissions_system_id_name
ON access_control.permissions (system_id, name);
