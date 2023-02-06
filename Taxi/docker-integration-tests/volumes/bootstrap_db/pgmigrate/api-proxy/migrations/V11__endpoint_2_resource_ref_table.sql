-- Extract relations between endpoints and resources and store them instead of using JSONB-based stored function

CREATE TABLE api_proxy.endpoint_resource_refs (
      endpoint_id       TEXT                    NOT NULL,
      endpoint_revision INTEGER                 NOT NULL,
      method            api_proxy.http_method_t NOT NULL,
      resource_id       TEXT                    NOT NULL,

      CONSTRAINT ep2res_pkey PRIMARY KEY (endpoint_id, endpoint_revision, resource_id, method),
      FOREIGN KEY (endpoint_id, endpoint_revision)
          REFERENCES api_proxy.endpoints(id, revision)
          ON DELETE CASCADE ON UPDATE RESTRICT
);

CREATE INDEX ep2res_refs_by_endpoint_index ON api_proxy.endpoint_resource_refs(endpoint_id, endpoint_revision);
CREATE INDEX ep2res_refs_by_resource_index ON api_proxy.endpoint_resource_refs(resource_id);

INSERT INTO api_proxy.endpoint_resource_refs(endpoint_id, endpoint_revision, method, resource_id)
SELECT DISTINCT id, revision, 'get'::api_proxy.http_method_t, source->>'resource'
FROM (
         SELECT id, revision, jsonb_array_elements(handler_get->'sources') AS source
         FROM api_proxy.endpoints
     ) AS sources;

INSERT INTO api_proxy.endpoint_resource_refs(endpoint_id, endpoint_revision, method, resource_id)
SELECT DISTINCT id, revision, 'post'::api_proxy.http_method_t, source->>'resource'
FROM (
         SELECT id, revision, jsonb_array_elements(handler_post->'sources') AS source
         FROM api_proxy.endpoints
     ) AS sources;

INSERT INTO api_proxy.endpoint_resource_refs(endpoint_id, endpoint_revision, method, resource_id)
SELECT DISTINCT id, revision, 'delete'::api_proxy.http_method_t, source->>'resource'
FROM (
         SELECT id, revision, jsonb_array_elements(handler_delete->'sources') AS source
         FROM api_proxy.endpoints
     ) AS sources;

INSERT INTO api_proxy.endpoint_resource_refs(endpoint_id, endpoint_revision, method, resource_id)
SELECT DISTINCT id, revision, 'put'::api_proxy.http_method_t, source->>'resource'
FROM (
         SELECT id, revision, jsonb_array_elements(handler_put->'sources') AS source
         FROM api_proxy.endpoints
     ) AS sources;

INSERT INTO api_proxy.endpoint_resource_refs(endpoint_id, endpoint_revision, method, resource_id)
SELECT DISTINCT id, revision, 'patch'::api_proxy.http_method_t, source->>'resource'
FROM (
         SELECT id, revision, jsonb_array_elements(handler_patch->'sources') AS source
         FROM api_proxy.endpoints
     ) AS sources;


--- Allow to seamlessly change handler column type

CREATE FUNCTION api_proxy.as_text(plain TEXT) RETURNS TEXT AS $$
BEGIN
    RETURN plain;
END
$$ LANGUAGE plpgsql;

CREATE FUNCTION api_proxy.as_text(json JSONB) RETURNS TEXT AS $$
BEGIN
    RETURN jsonb_pretty(json);
END
$$ LANGUAGE plpgsql;


CREATE FUNCTION api_proxy.as_handler(plain TEXT) RETURNS JSONB AS $$
BEGIN
    RETURN plain::jsonb;
END
$$ LANGUAGE plpgsql;

CREATE FUNCTION api_proxy.as_handler(json JSONB) RETURNS JSONB AS $$
BEGIN
    RETURN json;
END
$$ LANGUAGE plpgsql;

