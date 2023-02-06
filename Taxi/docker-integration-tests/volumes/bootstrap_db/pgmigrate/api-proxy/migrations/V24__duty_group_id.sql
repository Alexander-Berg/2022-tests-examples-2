--- Add duty_group_id and duty_abc
ALTER TABLE api_proxy.resources
    ADD COLUMN duty_group_id TEXT NULL DEFAULT NULL,
    ADD COLUMN duty_abc TEXT NULL DEFAULT NULL;

ALTER TABLE api_proxy.endpoints
    ADD COLUMN duty_group_id TEXT NULL DEFAULT NULL,
    ADD COLUMN duty_abc TEXT NULL DEFAULT NULL;
