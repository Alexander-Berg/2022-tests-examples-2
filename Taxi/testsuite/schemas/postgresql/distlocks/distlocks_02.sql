BEGIN TRANSACTION;

CREATE INDEX locks_expiration_time_idx ON distlocks.locks(expiration_time DESC);
ALTER TABLE distlocks.locks
    DROP CONSTRAINT locks_namespace_name_fkey,
    ADD CONSTRAINT locks_namespace_name_fkey
        FOREIGN KEY (namespace_name) REFERENCES distlocks.namespaces(name)
        ON DELETE CASCADE;

COMMIT TRANSACTION;
