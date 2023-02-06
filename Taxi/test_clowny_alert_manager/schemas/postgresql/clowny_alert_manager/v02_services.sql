CREATE TYPE alert_manager.service_type_e AS ENUM (
    'rtc',
    'cgroup',
    'qloud',
    'qloud-ext',
    'host'
);

-- Представляет из себя сервис, как независимую единицу,
-- объединяющую в себя все свои окружения
-- Должен маппится 1-1 к сервису в клоуне
CREATE TABLE alert_manager.services (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    clown_service_id INTEGER,
    clown_project_id INTEGER,
    service_name TEXT NOT NULL,
    project_name TEXT NOT NULL,
    type alert_manager.service_type_e NOT NULL,
    repo_meta alert_manager.repo_meta_t NOT NULL,

    CONSTRAINT deleted_without_delete_time CHECK ( is_deleted <> (deleted_at IS NULL) )
);

CREATE UNIQUE INDEX uniq_non_deleted_service_idx
    ON alert_manager.services(((repo_meta).config_project), project_name, service_name) WHERE NOT is_deleted;

CREATE TRIGGER alert_manager_services_set_updated
    BEFORE UPDATE
    ON alert_manager.services
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();

CREATE TRIGGER alert_manager_services_set_deleted
    BEFORE UPDATE
    ON alert_manager.services
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_deleted();

ALTER TABLE alert_manager.services
    ADD CONSTRAINT services_dangling_references
        CHECK (
            NOT (
                (clown_project_id::boolean AND NOT clown_service_id::boolean) OR
                (NOT clown_project_id::boolean AND clown_service_id::boolean)
            )
        );
CREATE UNIQUE INDEX uniq_clowny_service_id
    ON alert_manager.services(clown_service_id, ((repo_meta).config_project))
    WHERE NOT services.is_deleted AND clown_service_id IS NOT NULL;
