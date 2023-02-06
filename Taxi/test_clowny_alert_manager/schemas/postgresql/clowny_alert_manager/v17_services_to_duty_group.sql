BEGIN;

DROP TABLE IF EXISTS alert_manager.services_to_duty_group CASCADE;
CREATE TABLE alert_manager.services_to_duty_group (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    clown_service_id BIGINT NOT NULL,

    duty_group_id TEXT NOT NULL,

    CONSTRAINT deleted_without_delete_time CHECK (is_deleted <> (deleted_at IS NULL))
);

CREATE UNIQUE INDEX unique_non_deleted_services_to_duty_group_idx
    ON alert_manager.services_to_duty_group(clown_service_id) WHERE NOT is_deleted;

CREATE TRIGGER alert_manager_services_to_duty_group_set_updated
    BEFORE UPDATE
    ON alert_manager.services_to_duty_group
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();

CREATE TRIGGER alert_manager_services_to_duty_group_set_deleted
    BEFORE UPDATE
    ON alert_manager.services_to_duty_group
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_deleted();

COMMIT;
