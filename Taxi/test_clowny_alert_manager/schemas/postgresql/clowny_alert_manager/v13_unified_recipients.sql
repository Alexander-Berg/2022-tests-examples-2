-- Настройка получателей всех алертов бранча

BEGIN;

CREATE TABLE alert_manager.unified_recipients (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    branch_id BIGINT REFERENCES alert_manager.branches(id) ON DELETE RESTRICT,
    juggler_host_from_checkfile TEXT,

    chats TEXT[] NOT NULL,
    logins TEXT[] NOT NULL,
    duty TEXT NOT NULL DEFAULT 'off',
    do_merge_with_telegram_options BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT deleted_without_delete_time CHECK (is_deleted <> (deleted_at IS NULL)),
    CONSTRAINT has_connection CHECK ((branch_id IS NOT NULL) OR (juggler_host_from_checkfile IS NOT NULL))
);

CREATE UNIQUE INDEX unique_non_deleted_unified_recipients_to_branch_idx
    ON alert_manager.unified_recipients(branch_id) WHERE NOT is_deleted;

CREATE TRIGGER alert_manager_unified_recipients_set_updated
    BEFORE UPDATE
    ON alert_manager.unified_recipients
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();

CREATE TRIGGER alert_manager_unified_recipients_set_deleted
    BEFORE UPDATE
    ON alert_manager.unified_recipients
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_deleted();

COMMIT;
