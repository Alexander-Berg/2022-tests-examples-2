BEGIN;

DROP TABLE IF EXISTS alert_manager.duty_groups_info CASCADE;
CREATE TABLE alert_manager.duty_groups_info (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    group_id TEXT NOT NULL,

    duty_mode TEXT NOT NULL,
    dev_duty_start INTEGER,
    dev_duty_end INTEGER,
    telegram_options JSONB,
    abc_duty_group_slug TEXT,
    person_on_duty TEXT,
    all_duty_group_members TEXT[],

    CONSTRAINT deleted_without_delete_time CHECK (is_deleted <> (deleted_at IS NULL))
);

CREATE UNIQUE INDEX unique_non_deleted_duty_info_to_group_idx
    ON alert_manager.duty_groups_info(group_id) WHERE NOT is_deleted;

CREATE TRIGGER alert_manager_duty_info_set_updated
    BEFORE UPDATE
    ON alert_manager.duty_groups_info
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();

CREATE TRIGGER alert_manager_duty_info_set_deleted
    BEFORE UPDATE
    ON alert_manager.duty_groups_info
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_deleted();

COMMIT;
