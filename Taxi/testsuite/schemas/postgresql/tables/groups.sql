CREATE TABLE access_control.groups
(
    id                 SERIAL         NOT NULL PRIMARY KEY,
    parent_id          INTEGER        REFERENCES access_control.groups (id) ON DELETE CASCADE,
    parents            INTEGER[]      NOT NULL,
    name               TEXT           NOT NULL,
    slug               TEXT           NOT NULL,
    created_at         TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    system_id          INTEGER        NOT NULL REFERENCES access_control.system (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX groups_name_system_id ON access_control.groups (name, system_id);
CREATE UNIQUE INDEX groups_system_id_slug ON access_control.groups (system_id, slug);

CREATE TRIGGER groups_set_updated_at_timestamp
    BEFORE UPDATE ON access_control.groups
    FOR EACH ROW
EXECUTE PROCEDURE trigger_set_updated_at_timestamp();

CREATE TRIGGER groups_trigger_set_parents
    BEFORE INSERT OR UPDATE ON access_control.groups
    FOR EACH ROW
EXECUTE PROCEDURE trigger_set_parents();
