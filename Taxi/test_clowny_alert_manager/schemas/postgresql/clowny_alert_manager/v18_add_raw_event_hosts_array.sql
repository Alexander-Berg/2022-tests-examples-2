BEGIN;

ALTER TABLE alert_manager.alerts
    ADD COLUMN juggler_raw_event_hosts TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[];

UPDATE alert_manager.alerts
    SET juggler_raw_event_hosts = ARRAY[juggler_raw_event_host]::TEXT[];

ALTER TABLE alert_manager.alerts
    ADD CONSTRAINT non_empty_raw_event_hosts CHECK ( array_length(juggler_raw_event_hosts, 1) > 0 );

COMMIT;
