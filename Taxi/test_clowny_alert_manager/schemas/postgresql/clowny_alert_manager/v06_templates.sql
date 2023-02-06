-- Представляет из себя темплейт, объединение нескольких аггрегатов и подключаемый в любых бранчах
CREATE TABLE alert_manager.templates (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    repo_meta alert_manager.repo_meta_t NOT NULL,
    name TEXT NOT NULL,
    namespace TEXT NOT NULL,

    CONSTRAINT deleted_without_delete_time CHECK ( is_deleted <> (deleted_at IS NULL) )
);

CREATE UNIQUE INDEX uniq_non_deleted_template_idx
    ON alert_manager.templates(((repo_meta).config_project), name, namespace) WHERE NOT is_deleted;

CREATE TRIGGER alert_manager_templates_set_updated
    BEFORE UPDATE
    ON alert_manager.templates
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();

CREATE TRIGGER alert_manager_templates_set_deleted
    BEFORE UPDATE
    ON alert_manager.templates
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_deleted();

CREATE TYPE alert_manager.template_uniq_key_v1 AS (
    project TEXT,
    name TEXT,
    namespace TEXT
);
