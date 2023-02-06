DROP FUNCTION api_proxy.is_referred_to_resource;

CREATE FUNCTION api_proxy.is_referred_to_resource
(handler_config JSONB, resource_id TEXT) RETURNS BOOLEAN AS $$
DECLARE
  referred_resources INTEGER;
BEGIN
  SELECT COUNT(*) INTO referred_resources
  FROM jsonb_array_elements(handler_config->'sources') AS tmp
  WHERE (tmp.value->>'resource')::text = resource_id;

  RETURN referred_resources > 0;
END;
$$ LANGUAGE plpgsql;
