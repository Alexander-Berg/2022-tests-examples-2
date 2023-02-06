DROP SCHEMA IF EXISTS mia CASCADE;
CREATE SCHEMA mia;

CREATE TABLE mia.query(
    id bigserial PRIMARY KEY,
    priority integer DEFAULT 0,
    service_name text,
    status text,
    query text,
    queue text default 'common',
    created_time timestamp,
    started_time timestamp,
    finished_time timestamp
);

CREATE TABLE mia.result(
    id bigserial PRIMARY KEY,
    query_id bigserial UNIQUE,
    query_result jsonb NOT NULL,

    foreign key (query_id) references mia.query(id)
);

CREATE INDEX idx_service_name_and_status on mia.query(service_name, status);
