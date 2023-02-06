--- Endpoint cluster labels to be filtered during state load

-- drop foreign keys that depends on api_proxy.endpoints pkey and restore'em later
ALTER TABLE api_proxy.endpoints_control
    DROP CONSTRAINT endpoints_control_id_revision_fkey,
    DROP CONSTRAINT endpoints_control_prestable_fkey;
ALTER TABLE api_proxy.endpoint_resource_refs
    DROP CONSTRAINT IF EXISTS endpoint_resource_refs_endpoint_id_fkey,
    DROP CONSTRAINT IF EXISTS endpoint_resource_refs_endpoint_id_endpoint_revision_fkey;
ALTER TABLE api_proxy.snapshot_endpoints
    DROP CONSTRAINT snapshot_endpoints_endpoint_id_revision_fkey;

-- Migrate api_proxy.endpoints

ALTER TABLE api_proxy.endpoints
    ADD COLUMN cluster TEXT NOT NULL DEFAULT 'api-proxy';

ALTER TABLE api_proxy.endpoints
    DROP CONSTRAINT endpoints_pkey,
    ADD CONSTRAINT endpoints_pkey
        PRIMARY KEY (cluster, id, revision);

CREATE INDEX endpoints_cluster_id_index ON api_proxy.endpoints(cluster, id);

-- Migrate api_proxy.endpoints_control

ALTER TABLE api_proxy.endpoints_control
    ADD COLUMN cluster TEXT NOT NULL DEFAULT 'api-proxy';

ALTER TABLE api_proxy.endpoints_control
    DROP CONSTRAINT endpoints_control_pkey,
    ADD CONSTRAINT endpoints_control_pkey
        PRIMARY KEY (cluster, id),
    DROP CONSTRAINT endpoints_control_unique_path_cons,
    ADD CONSTRAINT endpoints_control_unique_path_cons
        UNIQUE (cluster, path);

ALTER TABLE api_proxy.endpoints_control -- garbage, duplicates pkey
    DROP CONSTRAINT endpoints_control_unique_id_revision_cons;

ALTER TABLE api_proxy.endpoints_control -- restore fkeys
    ADD CONSTRAINT endpoints_control_stable_fkey
        FOREIGN KEY (cluster, id, revision)
            REFERENCES api_proxy.endpoints(cluster, id, revision)
            ON DELETE RESTRICT ON UPDATE RESTRICT,
    ADD CONSTRAINT endpoints_control_prestable_fkey
        FOREIGN KEY (cluster, id, prestable_revision)
            REFERENCES api_proxy.endpoints(cluster, id, revision)
            ON DELETE SET NULL ON UPDATE RESTRICT;

-- Migrate api_proxy.endpoint_resource_refs

ALTER TABLE api_proxy.endpoint_resource_refs
    ADD COLUMN cluster TEXT NOT NULL DEFAULT 'api-proxy';

ALTER TABLE api_proxy.endpoint_resource_refs
    DROP CONSTRAINT ep2res_pkey,
    ADD CONSTRAINT ep2res_pkey
        PRIMARY KEY (cluster, endpoint_id, endpoint_revision, resource_id, method);

ALTER TABLE api_proxy.endpoint_resource_refs
    ADD CONSTRAINT endpoint_resource_refs_ep_fkey
        FOREIGN KEY (cluster, endpoint_id, endpoint_revision)
            REFERENCES api_proxy.endpoints(cluster, id, revision)
            ON UPDATE RESTRICT ON DELETE CASCADE;

CREATE INDEX ep2res_refs_by_ep_index
    ON api_proxy.endpoint_resource_refs(cluster, endpoint_id, endpoint_revision);


-- Migrate api_proxy.snapshot_endpoints

ALTER TABLE api_proxy.snapshot_endpoints
    ADD COLUMN cluster TEXT NOT NULL DEFAULT 'api-proxy';

ALTER TABLE api_proxy.snapshot_endpoints
    DROP CONSTRAINT snapshot_endpoints_pkey,
    ADD CONSTRAINT snapshot_endpoints_pkey
        PRIMARY KEY (snapshot_id, cluster, endpoint_id),
    DROP CONSTRAINT snapshot_endpoints_unique_triplet_cons,
    ADD CONSTRAINT snapshot_endpoints_unique_entity_cons
        UNIQUE (snapshot_id, cluster, endpoint_id, revision);


ALTER TABLE api_proxy.snapshot_endpoints
    ADD CONSTRAINT snapshot_endpoints_ep_fkey
        FOREIGN KEY (cluster, endpoint_id, revision)
            REFERENCES api_proxy.endpoints(cluster, id, revision)
            ON DELETE CASCADE ON UPDATE RESTRICT;

DROP INDEX api_proxy.snapshot_endpoints_search_index; -- never to be actually used
