--- Link resource revisions to git

ALTER TABLE api_proxy.resources
    ADD COLUMN git_commit_hash TEXT NULL DEFAULT NULL;
