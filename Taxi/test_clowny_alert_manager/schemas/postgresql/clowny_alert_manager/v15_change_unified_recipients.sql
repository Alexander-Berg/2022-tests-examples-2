-- Настройки получателей всех алертов сервиса

BEGIN;

DROP TABLE IF EXISTS alert_manager.unified_recipients CASCADE;
CREATE TABLE alert_manager.unified_recipients (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    clown_service_id BIGINT NOT NULL,

    chats TEXT[] NOT NULL,
    logins TEXT[] NOT NULL,
    duty TEXT NOT NULL DEFAULT 'off',
    receive_testing_alerts BOOLEAN NOT NULL DEFAULT FALSE,
    do_merge_with_telegram_options BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT deleted_without_delete_time CHECK (is_deleted <> (deleted_at IS NULL))
);

CREATE UNIQUE INDEX unique_non_deleted_unified_recipients_to_service_idx
    ON alert_manager.unified_recipients(clown_service_id) WHERE NOT is_deleted;

CREATE TRIGGER alert_manager_unified_recipients_set_updated
    BEFORE UPDATE
    ON alert_manager.unified_recipients
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();

CREATE TRIGGER alert_manager_unified_recipients_set_deleted
    BEFORE UPDATE
    ON alert_manager.unified_recipients
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_deleted();

COMMIT;
