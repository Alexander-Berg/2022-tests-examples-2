CREATE SCHEMA driver_license_queue;

CREATE TABLE driver_license_queue.requests(
    id VARCHAR(100) NOT NULL UNIQUE PRIMARY KEY,
    token TEXT,
    country TEXT,
    license_photo BYTEA,
    status TEXT,
    created TIMESTAMPTZ NOT NULL,
    updated TIMESTAMPTZ NOT NULL,
    retry_count integer NOT NULL DEFAULT 0
);

CREATE TABLE driver_license_queue.responses(
    id VARCHAR(100) NOT NULL UNIQUE PRIMARY KEY,
    due_date TEXT,
    first_name TEXT,
    last_name TEXT,
    middle_name TEXT,
    series TEXT,
    number TEXT,
    issue_date TEXT,
    country TEXT,
    created TIMESTAMPTZ NOT NULL
);

CREATE SCHEMA distlocks;

CREATE TABLE distlocks.proxy_ml(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);
