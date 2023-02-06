CREATE TABLE roles.roles (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL,
    fields jsonb,  -- https://wiki.yandex-team.ru/intranet/idm/API/#fields-data

    -- https://wiki.yandex-team.ru/intranet/idm/API/#node-params
    name roles.translatable_t NOT NULL,
    help roles.translatable_t NOT NULL,

    -- scope node (clownductor entity id), to which this role belongs
    external_ref_slug TEXT NOT NULL,
    ref_type roles.ref_type_e NOT NULL,

    subsystem_id BIGINT REFERENCES roles.subsystems(id) ON DELETE RESTRICT,

    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,

    CONSTRAINT slug_check CHECK ( slug ~ '^[a-z][a-z0-9\_\-\.]*$' ),
    -- system role cant be standalone
    CONSTRAINT non_system_standalone CHECK (
        CASE
            WHEN subsystem_id IS NULL THEN ref_type <> 'standalone'
            ELSE TRUE
        END
    )
);
CREATE UNIQUE INDEX subsystems_role_uniq_key_idx
    ON roles.roles(slug, external_ref_slug, ref_type, subsystem_id)
    WHERE NOT is_deleted AND subsystem_id IS NOT NULL;
CREATE UNIQUE INDEX systems_role_uniq_key_idx
    ON roles.roles(slug, external_ref_slug, ref_type)
    WHERE NOT is_deleted AND subsystem_id IS NULL;
CREATE TRIGGER roles_roles_set_updated
    BEFORE UPDATE OR INSERT ON roles.roles
    FOR EACH ROW EXECUTE PROCEDURE roles.set_updated();
CREATE TRIGGER roles_roles_set_deleted
    BEFORE UPDATE ON roles.roles
    FOR EACH ROW EXECUTE PROCEDURE roles.set_deleted();

CREATE FUNCTION roles.check_existing_abc_scope() RETURNS TRIGGER AS $check_existing_abc_scope$
    BEGIN
        IF NEW.ref_type = 'standalone' AND NOT exists(SELECT * FROM roles.abc_scopes AS s WHERE NOT s.is_deleted AND s.slug = NEW.external_ref_slug)
        THEN
            RAISE EXCEPTION 'abc scope(%) not exists for standalone type', NEW.external_ref_slug;
        END IF;
        RETURN NEW;
    END;
$check_existing_abc_scope$ LANGUAGE plpgsql;
CREATE TRIGGER roles_roles_check_existing_abc_scope
    BEFORE UPDATE OR INSERT ON roles.roles
    FOR EACH ROW EXECUTE PROCEDURE roles.check_existing_abc_scope();

CREATE FUNCTION roles.check_no_referencing_roles() RETURNS TRIGGER AS $check_no_referencing_roles$
    BEGIN
        IF TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND NEW.is_deleted)
        THEN
            IF exists(SELECT * FROM roles.roles AS r WHERE NOT r.is_deleted AND r.ref_type = 'standalone' AND r.external_ref_slug = OLD.slug)
            THEN
                RAISE EXCEPTION 'cant remove abc scope(%), cause there are some related roles', OLD.slug;
            END IF;
        END IF;

        IF TG_OP <> 'DELETE'
        THEN
            RETURN NEW;
        END IF;
    END;
$check_no_referencing_roles$ LANGUAGE plpgsql;
CREATE TRIGGER roles_abc_scopes_check_no_referencing_roles
    BEFORE DELETE OR UPDATE ON roles.abc_scopes
    FOR EACH ROW EXECUTE PROCEDURE roles.check_no_referencing_roles();

CREATE TYPE roles.role_v1 AS (
    id BIGINT,
    slug TEXT,
    fields jsonb,

    name roles.translatable_t,
    help roles.translatable_t,

    external_ref_slug TEXT,
    ref_type roles.ref_type_e,

    subsystem_id BIGINT,

    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    is_deleted BOOLEAN
);
