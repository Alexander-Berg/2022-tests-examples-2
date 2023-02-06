CREATE TABLE alert_manager.configs (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    branch_id BIGINT REFERENCES alert_manager.branches(id) ON DELETE RESTRICT NOT NULL,
    escalation_method alert_manager.escalation_method_e,
    responsibles TEXT[],
    repo_meta alert_manager.repo_meta_t NOT NULL,

    CONSTRAINT deleted_without_delete_time CHECK ( is_deleted <> (deleted_at IS NULL) )
);

CREATE UNIQUE INDEX uniq_non_deleted_config_idx
    ON alert_manager.configs(((repo_meta).file_path), branch_id) WHERE NOT is_deleted;

CREATE TRIGGER alert_manager_configs_set_updated
    BEFORE UPDATE
    ON alert_manager.configs
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_updated();

CREATE TRIGGER alert_manager_configs_set_deleted
    BEFORE UPDATE
    ON alert_manager.configs
    FOR EACH ROW EXECUTE PROCEDURE alert_manager.set_deleted();

CREATE TABLE alert_manager.configs_templates_m2m (
    id BIGSERIAL PRIMARY KEY,
    config_id BIGINT REFERENCES alert_manager.configs(id) ON DELETE RESTRICT NOT NULL,
    template_id BIGINT REFERENCES alert_manager.templates(id) ON DELETE RESTRICT NOT NULL,

    overrides alert_manager.overridable_settings_t NOT NULL,
    CONSTRAINT "overrides.ttl is greater then 15" CHECK ( (overrides).ttl >= 15 ),
    CONSTRAINT acceptable_refresh_time CHECK (
        ((overrides).active IS NULL) OR
        (
            (overrides).active IS NOT NULL AND
            (overrides).refresh_time <@ '[5, 300]'::int4range
        )
    ),

    UNIQUE (config_id, template_id)
);

CREATE TABLE alert_manager.configs_templates_notifications_m2m (
    id BIGSERIAL PRIMARY KEY,
    config_template_id BIGINT REFERENCES alert_manager.configs_templates_m2m(id) ON DELETE RESTRICT NOT NULL,
    notification_option_id BIGINT REFERENCES alert_manager.notification_options(id) ON DELETE RESTRICT NOT NULL,

    UNIQUE (config_template_id, notification_option_id)
);

CREATE TABLE alert_manager.configs_notifications_m2m (
    id BIGSERIAL PRIMARY KEY,
    config_id BIGINT REFERENCES alert_manager.configs(id) ON DELETE RESTRICT NOT NULL,
    notification_option_id BIGINT REFERENCES alert_manager.notification_options(id) ON DELETE RESTRICT NOT NULL,

    UNIQUE (config_id, notification_option_id)
);
