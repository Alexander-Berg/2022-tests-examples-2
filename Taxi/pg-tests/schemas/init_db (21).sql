CREATE SCHEMA loyalty;

CREATE TABLE loyalty.status_logs (
    log_id VARCHAR(255) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id)
);

