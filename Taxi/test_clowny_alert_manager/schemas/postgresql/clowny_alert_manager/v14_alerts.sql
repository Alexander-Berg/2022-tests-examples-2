CREATE TABLE alert_manager.alerts (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    service_id INTEGER,
    branch_id INTEGER,
    juggler_service TEXT NOT NULL,
    juggler_host TEXT NOT NULL,
    juggler_raw_event_host TEXT NOT NULL,
    recipients TEXT[] NOT NULL
        CONSTRAINT non_empty_recipients CHECK ( array_length(recipients, 1) > 0 ),

    CONSTRAINT deleted_without_delete_time CHECK ( is_deleted <> (deleted_at IS NULL) )
);

CREATE UNIQUE INDEX uniq_non_deleted_alert_idx
    ON alert_manager.alerts(juggler_service, juggler_host) WHERE NOT is_deleted;

CREATE TRIGGER alert_manager_alerts_set_updated
    BEFORE UPDATE
    ON alert_manager.alerts
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();

CREATE TRIGGER alert_manager_alerts_set_deleted
    BEFORE UPDATE
    ON alert_manager.alerts
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_deleted();
