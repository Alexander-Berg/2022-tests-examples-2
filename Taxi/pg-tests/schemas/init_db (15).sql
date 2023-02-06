CREATE SCHEMA order_log;

CREATE TABLE order_log.order_log
(
    order_id TEXT,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    can_be_archived BOOLEAN,
    PRIMARY KEY (order_id)
);

