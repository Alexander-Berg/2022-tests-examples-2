--- Removes endpoints_control_path_revision_key as non-relevant

ALTER TABLE api_proxy.endpoints_control
DROP CONSTRAINT IF EXISTS endpoints_control_path_revision_key;
