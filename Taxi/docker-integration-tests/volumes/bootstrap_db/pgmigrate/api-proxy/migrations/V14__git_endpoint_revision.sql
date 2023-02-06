--- Link endpoint revisions to git

ALTER TABLE api_proxy.endpoints
    ADD COLUMN git_commit_hash TEXT NULL DEFAULT NULL;
