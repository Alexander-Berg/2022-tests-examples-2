CREATE TABLE access_control.roles
(
    id                 SERIAL      NOT NULL PRIMARY KEY,
    name               TEXT        NOT NULL,
    slug               TEXT        NOT NULL,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    system_id          INTEGER     NOT NULL REFERENCES access_control.system (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX roles_name_system_id ON access_control.roles (name, system_id);
CREATE UNIQUE INDEX roles_system_id_slug ON access_control.roles (system_id, slug);
CREATE INDEX roles_slug ON access_control.roles (slug);

CREATE TRIGGER groups_set_updated_at_timestamp
    BEFORE UPDATE ON access_control.roles
    FOR EACH ROW
EXECUTE PROCEDURE trigger_set_updated_at_timestamp();
