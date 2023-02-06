--- Creates snapshot indexes to speedup admin operations

CREATE INDEX snapshot_endpoints_index_search
    ON api_proxy.snapshot_endpoints (cluster, endpoint_id, revision);
