CREATE TABLE roles.subsystems (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL,

    -- https://wiki.yandex-team.ru/intranet/idm/API/#node-params
    name roles.translatable_t NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,

    CONSTRAINT slug_check CHECK ( slug ~ '^[a-z][a-z0-9\_\-\.]*$' )
);
CREATE UNIQUE INDEX roles_subsystems_uniq_key_idx
    ON roles.subsystems(slug)
    WHERE NOT is_deleted;
CREATE TRIGGER roles_subsystems_set_updated
    BEFORE UPDATE OR INSERT ON roles.subsystems
    FOR EACH ROW EXECUTE PROCEDURE roles.set_updated();
CREATE TRIGGER roles_subsystems_set_deleted
    BEFORE UPDATE ON roles.subsystems
    FOR EACH ROW EXECUTE PROCEDURE roles.set_deleted();

CREATE TYPE roles.subsystem_v1 AS (
    id BIGINT,
    slug TEXT,

    name roles.translatable_t,

    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    is_deleted BOOLEAN
);
