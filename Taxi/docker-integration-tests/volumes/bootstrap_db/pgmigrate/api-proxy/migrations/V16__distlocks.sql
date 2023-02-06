--- Service table for cluster-level distibuted locks for storages::postgres::DistLockComponentBase

CREATE TABLE api_proxy.distlocks (
    key             TEXT PRIMARY KEY,
    owner           TEXT,
    expiration_time TIMESTAMPTZ
);
