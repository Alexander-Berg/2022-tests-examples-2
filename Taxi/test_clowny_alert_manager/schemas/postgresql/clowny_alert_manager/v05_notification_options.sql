CREATE TYPE alert_manager.notification_type_e AS ENUM (
    'telegram'
);

CREATE TYPE alert_manager.no_status_t AS (
    from_ alert_manager.alert_state_e,
    to_ alert_manager.alert_state_e
);

CREATE TABLE alert_manager.notification_options (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    repo_meta alert_manager.repo_meta_t NOT NULL,

    name TEXT NOT NULL,
    logins TEXT[] NOT NULL
        CONSTRAINT non_empty_logins CHECK ( array_length(logins, 1) > 0 ),
    statuses alert_manager.no_status_t[] NOT NULL
        CONSTRAINT non_empty_statuses CHECK ( array_length(statuses, 1) > 0 ),
    type alert_manager.notification_type_e NOT NULL
);

CREATE UNIQUE INDEX uniq_non_deleted_notification_option_idx
    ON alert_manager.notification_options(((repo_meta).config_project), type, name) WHERE NOT is_deleted;

CREATE TRIGGER alert_manager_notification_options_set_updated
    BEFORE UPDATE
    ON alert_manager.notification_options
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();
CREATE TRIGGER alert_manager_notification_options_set_deleted
    BEFORE UPDATE
    ON alert_manager.notification_options
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_deleted();
