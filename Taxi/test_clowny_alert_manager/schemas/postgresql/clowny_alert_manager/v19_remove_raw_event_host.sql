BEGIN;

ALTER TABLE alert_manager.alerts
    DROP COLUMN juggler_raw_event_host;

COMMIT;
