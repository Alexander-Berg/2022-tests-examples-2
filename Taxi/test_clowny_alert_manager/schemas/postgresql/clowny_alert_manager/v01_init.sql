CREATE SCHEMA alert_manager;

CREATE FUNCTION alert_manager.set_updated() RETURNS TRIGGER AS $set_updated$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
$set_updated$ LANGUAGE plpgsql;

CREATE FUNCTION alert_manager.set_deleted() RETURNS TRIGGER AS $set_deleted$
    BEGIN
        IF NEW.is_deleted AND NOT OLD.is_deleted THEN NEW.deleted_at = NOW(); END IF;
        IF NOT NEW.is_deleted AND OLD.is_deleted THEN NEW.deleted_at = NULL; END IF;
        RETURN NEW;
    END;
$set_deleted$ LANGUAGE plpgsql;

CREATE TYPE alert_manager.repo_meta_t AS (
    file_path TEXT,
    file_name TEXT,
    config_project TEXT
);
