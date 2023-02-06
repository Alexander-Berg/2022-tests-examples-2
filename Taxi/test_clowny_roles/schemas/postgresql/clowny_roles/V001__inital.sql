CREATE SCHEMA roles;

CREATE FUNCTION roles.set_updated() RETURNS TRIGGER AS $set_updated$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
$set_updated$ LANGUAGE plpgsql;

CREATE FUNCTION roles.set_deleted() RETURNS TRIGGER AS $set_deleted$
    BEGIN
        IF NEW.is_deleted AND NOT OLD.is_deleted THEN NEW.deleted_at = now(); END IF;
        IF NOT NEW.is_deleted AND OLD.is_deleted THEN NEW.deleted_at = NULL; END IF;
        RETURN NEW;
    END;
$set_deleted$ LANGUAGE plpgsql;

CREATE TYPE roles.ref_type_e AS ENUM ('namespace', 'project', 'service', 'standalone');

CREATE TYPE roles.translatable_t AS (
    en TEXT,
    ru TEXT
);
