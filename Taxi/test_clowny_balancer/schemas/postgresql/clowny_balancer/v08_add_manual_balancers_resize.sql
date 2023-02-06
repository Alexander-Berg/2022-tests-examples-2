CREATE TYPE balancers.manual_resize_status_t AS ENUM (
    'in_progress',
    'success',
    'failed',
    'cancelled'
);

CREATE TABLE balancers.manual_resize (
    id TEXT PRIMARY KEY,
    tp_job_id INT UNIQUE,
    idempotency_token TEXT UNIQUE NOT NULL,
    status balancers.manual_resize_status_t NOT NULL,
    namespace_id TEXT NOT NULL,
    parameters JSONB NOT NULL
);

CREATE UNIQUE INDEX namespace_id_in_progress_unique
    ON balancers.manual_resize (
        namespace_id
    )
    WHERE status = 'in_progress'
;
