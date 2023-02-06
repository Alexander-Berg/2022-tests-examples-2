DROP SCHEMA IF EXISTS grabber CASCADE;
CREATE SCHEMA grabber;

CREATE TABLE grabber.tasks
(
    task_id                     TEXT PRIMARY KEY,
    order_id                    TEXT,
    partner_order_id            TEXT,
    driver_uuid                 TEXT,
    driver_device_id            TEXT,
    driver_metrica_uuid         TEXT,
    start_time                  timestamp WITH TIME ZONE,
    end_time                    timestamp WITH TIME ZONE,
    created                     timestamp WITH TIME ZONE NOT NULL default NOW(),
    updated                     timestamp WITH TIME ZONE NOT NULL default NOW(),
    author                      TEXT
);

CREATE TYPE grabber.operation_status AS ENUM
(
    'created',
    'processing',
    'finished',
    'cancelled',
    'failed'
);

CREATE TYPE grabber.operation_type AS ENUM
(
    'yql_query'
);

CREATE TABLE grabber.operations
(
    operation_id                TEXT PRIMARY KEY,
    operation_type              grabber.operation_type NOT NULL,
    error_message               TEXT,
    operation_status            grabber.operation_status NOT NULL,
    task_id                     TEXT REFERENCES grabber.tasks (task_id) ON DELETE CASCADE,
    operation_data_type         TEXT
);

CREATE TABLE grabber.operations_data
(
    operation_id           TEXT REFERENCES grabber.operations (operation_id) ON DELETE CASCADE,
    json_data              JSONB
);


CREATE TABLE grabber.yql_operations
(
    operation_id        TEXT REFERENCES grabber.operations (operation_id) ON DELETE CASCADE,
    yql_operation_id    TEXT,
    yql_query           TEXT,
    yql_share_url       TEXT
);

CREATE TABLE grabber.data_requests
(
    request_id                  TEXT PRIMARY KEY,
    task_id                     TEXT REFERENCES grabber.tasks (task_id) ON DELETE CASCADE,
    data_type                    TEXT,
    data_filter                 JSONB,
    operation_id                TEXT REFERENCES grabber.operations (operation_id)
);
