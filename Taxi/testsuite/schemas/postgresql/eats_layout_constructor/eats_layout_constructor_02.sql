BEGIN TRANSACTION;

ALTER TABLE constructor.layout_widgets ADD COLUMN meta_widget
    BIGINT REFERENCES constructor.meta_widgets(id) ON DELETE RESTRICT
    DEFAULT NULL;

CREATE TYPE constructor.layout_widget_v2 AS (
    url_id INTEGER,
    widget_template_id BIGINT,
    name TEXT,
    type TEXT,
    template_meta JSONB,
    meta JSONB,
    payload_schema JSONB,
    template_payload JSONB,
    payload JSONB,
    meta_widget BIGINT
);

COMMIT TRANSACTION;
