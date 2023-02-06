CREATE TABLE processing.tasks(
    scope           TEXT        NOT NULL,
    single_pipeline TEXT        NOT NULL,

    created         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    due             TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    payload         JSONB       NULL DEFAULT NULL,
    item_id         TEXT        NOT NULL,
    need_handle     BOOLEAN     NOT NULL DEFAULT TRUE,

    idempotency_token TEXT,

    PRIMARY KEY (scope, single_pipeline, item_id)
);

CREATE INDEX processing_pipelines_for_replications_idx
ON processing.tasks(updated ASC);

CREATE TYPE processing.task_locator_v1 AS (
    scope    TEXT,
    single_pipeline    TEXT,
    item_id  TEXT
    );

CREATE TYPE processing.pipeline_task_v1 AS (
    item_id     TEXT,
    created     TIMESTAMPTZ,
    updated     TIMESTAMPTZ,
    need_handle BOOLEAN,
    payload     JSONB
    );

CREATE TYPE processing.new_task_v1 AS (
    scope TEXT,
    single_pipeline TEXT,
    item_id TEXT,
    idempotency_token TEXT,
    due TIMESTAMPTZ
);
