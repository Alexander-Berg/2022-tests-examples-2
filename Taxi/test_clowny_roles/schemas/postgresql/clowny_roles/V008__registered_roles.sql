CREATE TABLE roles.registered_roles (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL,
    scopes roles.ref_type_e[] NOT NULL,
    fields jsonb,  -- https://wiki.yandex-team.ru/intranet/idm/API/#fields-data

    -- https://wiki.yandex-team.ru/intranet/idm/API/#node-params
    name roles.translatable_t NOT NULL,
    help roles.translatable_t NOT NULL,

    subsystem_id BIGINT REFERENCES roles.subsystems(id) ON DELETE RESTRICT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,

    CONSTRAINT slug_check CHECK ( slug ~ '^[a-z][a-z0-9\_\-\.]*$' )
);

CREATE UNIQUE INDEX roles_registered_non_deleted
    ON roles.registered_roles(slug, subsystem_id) WHERE NOT is_deleted;
CREATE TRIGGER roles_registered_roles_set_updated
    BEFORE UPDATE OR INSERT ON roles.registered_roles
    FOR EACH ROW EXECUTE PROCEDURE roles.set_updated();
CREATE TRIGGER roles_registered_roles_set_deleted
    BEFORE UPDATE ON roles.registered_roles
    FOR EACH ROW EXECUTE PROCEDURE roles.set_deleted();

CREATE TABLE roles.registered_roles_includes (
    main_role_id BIGINT NOT NULL REFERENCES roles.registered_roles(id) ON DELETE CASCADE,
    included_role_id BIGINT NOT NULL REFERENCES roles.registered_roles(id) ON DELETE CASCADE,
    UNIQUE (main_role_id, included_role_id)
);
