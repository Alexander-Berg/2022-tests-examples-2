BEGIN;

ALTER TABLE alert_manager.unified_recipients
    ADD COLUMN testing_chats TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[];

COMMIT;
