--- Restrict endpoints clusters to be explicitly set

ALTER TABLE api_proxy.endpoints
    ALTER COLUMN cluster DROP DEFAULT;

ALTER TABLE api_proxy.endpoints_control
    ALTER COLUMN cluster DROP DEFAULT;

ALTER TABLE api_proxy.endpoint_resource_refs
    ALTER COLUMN cluster DROP DEFAULT;

ALTER TABLE api_proxy.snapshot_endpoints
    ALTER COLUMN cluster DROP DEFAULT;
