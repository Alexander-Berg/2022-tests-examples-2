ALTER TABLE api_proxy.resources ADD COLUMN rps_limit INTEGER NULL DEFAULT NULL CHECK(rps_limit >= 0);
