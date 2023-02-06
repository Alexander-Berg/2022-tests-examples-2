CREATE SCHEMA api_proxy;

-- Resources

CREATE TYPE api_proxy.http_method_t AS ENUM (
  'get',
  'post',
  'delete',
  'put',
  'patch'
  );

CREATE TABLE api_proxy.resources
(
  id                      TEXT                    NOT NULL,
  revision                INTEGER                 NOT NULL DEFAULT 0,
  created                 TIMESTAMPTZ             NOT NULL DEFAULT NOW(),

  url                     TEXT                    NOT NULL,
  tvm_name                TEXT                    NULL,
  method                  api_proxy.http_method_t NOT NULL,

  timeout                 INTEGER                 NULL CHECK(timeout >= 0),
  timeout_taxi_config     TEXT                    NULL DEFAULT NULL,
  max_retries             INTEGER                 NULL CHECK(max_retries >= 0),
  max_retries_taxi_config TEXT                    NULL DEFAULT NULL,

  summary                 TEXT                    NOT NULL,

  PRIMARY KEY (id, revision)
);


CREATE INDEX resource_id_index ON api_proxy.resources (id);

CREATE TABLE api_proxy.resources_control
(
  id       TEXT        NOT NULL,
  revision INTEGER     NOT NULL,
  updated  TIMESTAMPTZ NOT NULL,

  CONSTRAINT resources_control_pk_constraint PRIMARY KEY(id),
  UNIQUE(id, revision),
  FOREIGN KEY(id, revision)
    REFERENCES api_proxy.resources(id, revision)
    ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Endpoints

CREATE TABLE api_proxy.endpoints
(
  path           TEXT        NOT NULL,
  revision       INTEGER     NOT NULL DEFAULT 0,
  created        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  handler_get    JSONB       NULL DEFAULT NULL,
  handler_post   JSONB       NULL DEFAULT NULL,
  handler_put    JSONB       NULL DEFAULT NULL,
  handler_patch  JSONB       NULL DEFAULT NULL,
  handler_delete JSONB       NULL DEFAULT NULL,

  enabled        BOOLEAN     NOT NULL DEFAULT FALSE,
  summary        TEXT        NOT NULL,
  maintainers    TEXT[]      NOT NULL,

  PRIMARY KEY (path, revision)
);

CREATE INDEX endpoints_id_index ON api_proxy.endpoints (path);

CREATE TABLE api_proxy.endpoints_control
(
  path     TEXT        NOT NULL,
  revision INTEGER     NOT NULL,
  updated  TIMESTAMPTZ NOT NULL,

  CONSTRAINT endpoints_control_pk_contratint PRIMARY KEY(path),
  UNIQUE(path, revision),
  CONSTRAINT endpoints_control_path_fkey FOREIGN KEY(path, revision)
    REFERENCES api_proxy.endpoints(path, revision)
    ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Snapshots

CREATE TABLE api_proxy.snapshots
(
  id      BIGSERIAL   NOT NULL PRIMARY KEY,
  created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  comment TEXT        NULL DEFAULT NULL
);

CREATE TABLE api_proxy.snapshot_resources
(
  snapshot_id BIGINT  NOT NULL REFERENCES api_proxy.snapshots(id)
    ON UPDATE RESTRICT ON DELETE CASCADE,
  resource_id TEXT    NOT NULL,
  revision    INTEGER NOT NULL,

  PRIMARY KEY(snapshot_id, resource_id),
  UNIQUE(snapshot_id, resource_id, revision),
  FOREIGN KEY(resource_id, revision)
    REFERENCES api_proxy.resources(id, revision)
    ON DELETE CASCADE ON UPDATE RESTRICT
);

CREATE INDEX snapshot_resources_index_search
  ON api_proxy.snapshot_resources (resource_id, revision);

CREATE TABLE api_proxy.snapshot_endpoints
(
  snapshot_id   BIGINT  NOT NULL REFERENCES api_proxy.snapshots(id)
    ON UPDATE RESTRICT ON DELETE CASCADE,
  endpoint_path TEXT    NOT NULL,
  revision      INTEGER NOT NULL,

  PRIMARY KEY(snapshot_id, endpoint_path),
  UNIQUE(snapshot_id, endpoint_path, revision),
  CONSTRAINT snapshot_endpoints_endpoint_path_fkey FOREIGN KEY(endpoint_path, revision)
    REFERENCES api_proxy.endpoints(path, revision)
    ON DELETE CASCADE ON UPDATE RESTRICT
);

CREATE INDEX snapshot_endpoints_index_search
  ON api_proxy.snapshot_endpoints (endpoint_path, revision);

-- Miscellaneous

CREATE FUNCTION api_proxy.is_referred_to_resource
(handler_config JSONB, resource_id TEXT) RETURNS BOOLEAN AS $$
DECLARE
  referred_resources INTEGER;
BEGIN
  SELECT COUNT(*) INTO referred_resources
  FROM jsonb_each(handler_config->'sources') AS tmp
  WHERE (tmp.value->>'resource')::text = resource_id;

  RETURN referred_resources > 0;
END;
$$ LANGUAGE plpgsql;
