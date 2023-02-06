/* add grants for taxiro */

DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'taxiro') THEN
            GRANT USAGE ON SCHEMA fts_indexer TO taxiro;
            GRANT SELECT ON ALL TABLES IN SCHEMA fts_indexer TO taxiro;
            ALTER DEFAULT PRIVILEGES IN SCHEMA fts_indexer GRANT SELECT ON TABLES TO taxiro;
        END IF;
    END
$$;
