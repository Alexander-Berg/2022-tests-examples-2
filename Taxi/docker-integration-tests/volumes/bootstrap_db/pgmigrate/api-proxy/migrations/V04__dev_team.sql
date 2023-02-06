ALTER TABLE api_proxy.resources
  ADD COLUMN dev_team TEXT NOT NULL DEFAULT 'ordercycle';

ALTER TABLE api_proxy.endpoints
  ADD COLUMN dev_team TEXT NOT NULL DEFAULT 'ordercycle';

ALTER TABLE api_proxy.endpoints
  ALTER COLUMN maintainers SET DEFAULT ARRAY[''];
