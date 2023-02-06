BEGIN TRANSACTION;

ALTER TABLE constructor.layout_widgets ADD COLUMN meta_widget_experiment_name
    TEXT DEFAULT NULL;

CREATE TYPE constructor.layout_widget_v3 AS (
    url_id INTEGER,
    widget_template_id BIGINT,
    name TEXT,
    type TEXT,
    template_meta JSONB,
    meta JSONB,
    payload_schema JSONB,
    template_payload JSONB,
    payload JSONB,
    meta_widget BIGINT,
    meta_widget_experiment_name TEXT
);

COMMIT TRANSACTION;
