CREATE TABLE meta.service_locks (
    service_id INTEGER UNIQUE NOT NULL,
    owner TEXT NOT NULL,
    ttl TIMESTAMP NOT NULL
);
