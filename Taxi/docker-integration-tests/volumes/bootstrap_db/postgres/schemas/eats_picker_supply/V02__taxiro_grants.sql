DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'taxiro') THEN
        GRANT USAGE ON SCHEMA eats_picker_supply TO taxiro;
        GRANT SELECT ON ALL TABLES IN SCHEMA eats_picker_supply TO taxiro;
        ALTER DEFAULT PRIVILEGES IN SCHEMA eats_picker_supply GRANT SELECT ON TABLES TO taxiro;
    END IF;
END $$;
