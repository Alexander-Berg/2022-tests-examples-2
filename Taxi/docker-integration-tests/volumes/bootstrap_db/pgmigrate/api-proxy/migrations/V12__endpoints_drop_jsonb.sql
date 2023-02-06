--- No more JSONB in handlers

ALTER TABLE api_proxy.endpoints ALTER COLUMN handler_get
    SET DATA TYPE TEXT USING jsonb_pretty(handler_get);
ALTER TABLE api_proxy.endpoints ALTER COLUMN handler_post
    SET DATA TYPE TEXT USING jsonb_pretty(handler_post);
ALTER TABLE api_proxy.endpoints ALTER COLUMN handler_delete
    SET DATA TYPE TEXT USING jsonb_pretty(handler_delete);
ALTER TABLE api_proxy.endpoints ALTER COLUMN handler_put
    SET DATA TYPE TEXT USING jsonb_pretty(handler_put);
ALTER TABLE api_proxy.endpoints ALTER COLUMN handler_patch
    SET DATA TYPE TEXT USING jsonb_pretty(handler_patch);

-- Cleanups and adapt typecasts

DROP FUNCTION api_proxy.is_referred_to_resource;
DROP FUNCTION api_proxy.as_handler(TEXT);
DROP FUNCTION api_proxy.as_handler(JSONB);

CREATE FUNCTION api_proxy.as_handler(plain TEXT) RETURNS TEXT AS $$
BEGIN
    RETURN plain;
END
$$ LANGUAGE plpgsql;
