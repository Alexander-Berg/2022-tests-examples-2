CREATE SCHEMA permissions;

CREATE FUNCTION permissions.set_updated() RETURNS TRIGGER AS $set_updated$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
$set_updated$ LANGUAGE plpgsql;

CREATE FUNCTION permissions.set_deleted() RETURNS TRIGGER AS $set_deleted$
    BEGIN
        IF NEW.is_deleted AND NOT OLD.is_deleted THEN NEW.deleted_at = NOW(); END IF;
        IF NOT NEW.is_deleted AND OLD.is_deleted THEN NEW.deleted_at = NULL; END IF;
        RETURN NEW;
    END;
$set_deleted$ LANGUAGE plpgsql;

CREATE FUNCTION permissions.service_project_deleted() RETURNS TRIGGER AS $service_project_deleted$
    BEGIN
        IF OLD.project_id IS NOT NULL AND NEW.project_id IS NULL
            THEN
                NEW.deleted_project = OLD.project_id;
                NEW.is_deleted = TRUE;
        END IF;
        IF OLD.service_id IS NOT NULL AND NEW.service_id IS NULL
            THEN
                NEW.deleted_service = OLD.service_id;
                NEW.is_deleted = TRUE;
        END IF;
        RETURN NEW;
    END;
$service_project_deleted$ LANGUAGE plpgsql;

CREATE TABLE permissions.roles (
    id BIGSERIAL PRIMARY KEY,
    role TEXT NOT NULL,
    login TEXT NOT NULL,

    project_id BIGINT REFERENCES clownductor.projects(id) ON DELETE SET NULL,
    service_id BIGINT REFERENCES clownductor.services(id) ON DELETE SET NULL,

    deleted_project BIGINT DEFAULT NULL,
    deleted_service BIGINT DEFAULT NULL,

    fired BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE UNIQUE INDEX uniq_login_role_project_idx
    ON permissions.roles(login, role, project_id)
    WHERE NOT is_deleted AND project_id IS NOT NULL;

CREATE UNIQUE INDEX uniq_login_role_service_idx
    ON permissions.roles(login, role, service_id)
    WHERE NOT is_deleted AND service_id IS NOT NULL;

ALTER TABLE permissions.roles
    ADD CONSTRAINT check_fired_is_deleted CHECK ( NOT fired OR fired AND is_deleted),
    ADD CONSTRAINT check_deleted_with_time CHECK ( is_deleted <> (deleted_at IS NULL) ),
    ADD CONSTRAINT check_exclusive_project_or_service
        CHECK (
            (project_id IS NOT NULL OR deleted_project IS NOT NULL) <>
            (service_id IS NOT NULL OR deleted_service IS NOT NULL)
        )
;

CREATE TRIGGER permissions_role_set_updated BEFORE UPDATE OR INSERT ON permissions.roles
    FOR EACH ROW EXECUTE PROCEDURE permissions.set_updated();
CREATE TRIGGER permissions_role_set_deleted BEFORE UPDATE ON permissions.roles
    FOR EACH ROW EXECUTE PROCEDURE permissions.set_deleted();
CREATE TRIGGER permissions_role_delete_reference BEFORE UPDATE ON permissions.roles
    FOR EACH ROW EXECUTE PROCEDURE permissions.service_project_deleted();
