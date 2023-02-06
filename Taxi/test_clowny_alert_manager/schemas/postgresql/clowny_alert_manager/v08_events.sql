-- Представляет из себя настройку аггрегата события, который описывается в файле настроек бранча или темплейта
CREATE TABLE alert_manager.events (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    name TEXT NOT NULL,
    config_id BIGINT REFERENCES alert_manager.configs(id) ON DELETE RESTRICT,
    template_id BIGINT REFERENCES alert_manager.templates(id) ON DELETE RESTRICT,

    settings alert_manager.overridable_settings_t NOT NULL,

    CONSTRAINT "settings.ignore_nodata is not null" CHECK ( (settings).ignore_nodata IS NOT NULL ),
    CONSTRAINT "settings.ttl is greater then 15" CHECK ( (settings).ttl >= 15 ),
    CONSTRAINT non_empty_times CHECK (
        (settings).times IS NOT NULL AND
        array_length((settings).times, 1) > 0
    ),
    CONSTRAINT acceptable_refresh_time CHECK (
        ((settings).active IS NULL) OR
        (
            (settings).active IS NOT NULL AND
            (settings).refresh_time <@ '[5, 300]'::int4range
        )
    ),

    CONSTRAINT non_dangling CHECK (
        (config_id IS NULL) <> (template_id IS NULL) AND
        (config_id IS NOT NULL) <> (template_id IS NOT NULL)
    ),
    CONSTRAINT deleted_without_delete_time CHECK ( is_deleted <> (deleted_at IS NULL) )
);

CREATE UNIQUE INDEX uniq_non_deleted_event_for_config_idx
    ON alert_manager.events(name, config_id) WHERE NOT is_deleted AND events.config_id IS NOT NULL;
CREATE UNIQUE INDEX uniq_non_deleted_event_for_template_idx
    ON alert_manager.events(name, template_id) WHERE NOT is_deleted AND events.template_id IS NOT NULL;

CREATE TRIGGER alert_manager_events_set_updated
    BEFORE UPDATE
    ON alert_manager.events
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();
CREATE TRIGGER alert_manager_events_set_deleted
    BEFORE UPDATE
    ON alert_manager.events
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_deleted();

CREATE TABLE alert_manager.events_notifications_m2m (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT REFERENCES alert_manager.events(id) ON DELETE RESTRICT NOT NULL,
    notification_option_id BIGINT REFERENCES alert_manager.notification_options(id) ON DELETE RESTRICT NOT NULL,

    UNIQUE (event_id, notification_option_id)
);
