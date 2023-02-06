-- Migrate api_proxy.endpoints to new pkey that does not depend on path
-- 1. Drop dependent references for api_proxy.endpoints pkey

ALTER TABLE api_proxy.endpoints_control DROP CONSTRAINT api_proxy_endpoints_control_prestable_fk;
ALTER TABLE api_proxy.endpoints_control DROP CONSTRAINT endpoints_control_path_fkey;
ALTER TABLE api_proxy.snapshot_endpoints DROP CONSTRAINT snapshot_endpoints_endpoint_path_fkey;

-- 2. Migrate api_proxy.endpoints

ALTER TABLE api_proxy.endpoints
  ADD COLUMN id TEXT;

UPDATE api_proxy.endpoints
SET id = path;

ALTER TABLE api_proxy.endpoints
  ALTER COLUMN id SET NOT NULL;

ALTER TABLE api_proxy.endpoints
  DROP CONSTRAINT endpoints_pkey,
  ADD CONSTRAINT endpoints_pkey
    PRIMARY KEY (id, revision);

ALTER INDEX api_proxy.endpoints_id_index RENAME TO endpoints_path_index;
CREATE INDEX endpoints_id_index ON api_proxy.endpoints (id);

-- 3. Migrate api_proxy.endpoints_control

ALTER TABLE api_proxy.endpoints_control
  ADD COLUMN id TEXT;

UPDATE api_proxy.endpoints_control
SET id = path;

ALTER TABLE api_proxy.endpoints_control
  ALTER COLUMN id SET NOT NULL;

ALTER TABLE api_proxy.endpoints_control
  DROP CONSTRAINT endpoints_control_pk_contratint;

ALTER TABLE api_proxy.endpoints_control
  ADD CONSTRAINT endpoints_control_pkey
    PRIMARY KEY (id),
  ADD CONSTRAINT endpoints_control_unique_id_revision_cons
    UNIQUE (id, revision),
  ADD CONSTRAINT endpoints_control_id_revision_fkey
    FOREIGN KEY (id, revision)
      REFERENCES api_proxy.endpoints(id, revision)
      ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT endpoints_control_prestable_fkey
    FOREIGN KEY (id, prestable_revision)
      REFERENCES api_proxy.endpoints(id, revision)
      ON DELETE SET NULL ON UPDATE RESTRICT,
  ADD CONSTRAINT endpoints_control_unique_path_cons
    UNIQUE (path);

CREATE INDEX endpoints_control_path_index ON api_proxy.endpoints_control (path);

-- 4. Migrate api_proxy.snapshot_endpoints

ALTER TABLE api_proxy.snapshot_endpoints
  ADD COLUMN endpoint_id TEXT;

UPDATE api_proxy.snapshot_endpoints
SET endpoint_id = endpoint_path;

ALTER TABLE api_proxy.snapshot_endpoints
  ALTER COLUMN endpoint_id SET NOT NULL;

ALTER TABLE api_proxy.snapshot_endpoints
  DROP CONSTRAINT snapshot_endpoints_pkey,
  DROP CONSTRAINT snapshot_endpoints_snapshot_id_endpoint_path_revision_key;

ALTER TABLE api_proxy.snapshot_endpoints
  DROP COLUMN  endpoint_path;

ALTER TABLE api_proxy.snapshot_endpoints
  ADD CONSTRAINT snapshot_endpoints_pkey
    PRIMARY KEY (snapshot_id, endpoint_id),
  ADD CONSTRAINT snapshot_endpoints_endpoint_id_revision_fkey
    FOREIGN KEY (endpoint_id, revision)
      REFERENCES api_proxy.endpoints(id, revision)
      ON DELETE CASCADE ON UPDATE RESTRICT,
  ADD CONSTRAINT snapshot_endpoints_unique_triplet_cons
    UNIQUE (snapshot_id, endpoint_id, revision);

CREATE INDEX snapshot_endpoints_search_index
  ON api_proxy.snapshot_endpoints (endpoint_id, revision);
