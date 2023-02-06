ALTER TABLE api_proxy.resources_control
  ADD COLUMN prestable_revision INTEGER NULL DEFAULT NULL;

ALTER TABLE api_proxy.resources_control
  ADD COLUMN prestable_percent INTEGER NULL DEFAULT NULL;

ALTER TABLE api_proxy.resources_control
  ADD CONSTRAINT api_proxy_resources_control_prestable_fk
    FOREIGN KEY(id, prestable_revision)
      REFERENCES api_proxy.resources(id, revision)
      ON DELETE SET NULL ON UPDATE RESTRICT;

ALTER TABLE api_proxy.resources_control
  ADD CONSTRAINT api_proxy_resources_control_prestable_check_nulls
    CHECK ((prestable_percent IS NULL     AND prestable_revision IS NULL)
      OR (prestable_percent IS NOT NULL AND prestable_revision IS NOT NULL));

ALTER TABLE api_proxy.resources_control
  ADD CONSTRAINT api_proxy_resources_control_prestable_check_percent
    CHECK (prestable_percent IS NULL OR prestable_percent BETWEEN 1 AND 99);

--

ALTER TABLE api_proxy.endpoints_control
  ADD COLUMN prestable_revision INTEGER NULL DEFAULT NULL;

ALTER TABLE api_proxy.endpoints_control
  ADD COLUMN prestable_percent INTEGER NULL DEFAULT NULL;

ALTER TABLE api_proxy.endpoints_control
  ADD CONSTRAINT api_proxy_endpoints_control_prestable_fk
    FOREIGN KEY(path, prestable_revision)
      REFERENCES api_proxy.endpoints(path, revision)
      ON DELETE SET NULL ON UPDATE RESTRICT;

ALTER TABLE api_proxy.endpoints_control
  ADD CONSTRAINT api_proxy_endpoints_control_prestable_check_nulls
    CHECK ((prestable_percent IS NULL     AND prestable_revision IS NULL)
      OR (prestable_percent IS NOT NULL AND prestable_revision IS NOT NULL));

ALTER TABLE api_proxy.endpoints_control
  ADD CONSTRAINT api_proxy_endpoints_control_prestable_check_percent
    CHECK (prestable_percent IS NULL OR prestable_percent BETWEEN 1 AND 99);
