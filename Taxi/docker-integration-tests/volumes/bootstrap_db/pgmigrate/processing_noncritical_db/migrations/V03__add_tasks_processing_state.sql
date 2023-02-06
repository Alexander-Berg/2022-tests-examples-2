CREATE TABLE processing_noncritical.processing_tasks_state_v1(
    scope                  TEXT        NOT NULL,
    single_pipeline        TEXT        NOT NULL,
    item_id                TEXT        NOT NULL,
    shared_state_bson      BYTEA       NULL,
    stage                  TEXT        NULL,
    finished_handlers      TEXT[]      NULL,
    handlers_result_bson   BYTEA       NULL,
    state_version          TEXT        NULL,

    PRIMARY KEY(scope, single_pipeline, item_id)
);

CREATE TYPE processing_noncritical.processing_tasks_state_upsert_v1 AS (
    shared_state_bson      BYTEA,
    stage                  TEXT,
    finished_handlers      TEXT[],
    handlers_result_bson   BYTEA
);

CREATE TYPE processing_noncritical.task_locator_v1 AS (
    scope    TEXT,
    single_pipeline    TEXT,
    item_id  TEXT
);
