START TRANSACTION;

CREATE TABLE clownductor.balancers (
    id SERIAL UNIQUE PRIMARY KEY,
    awacs_namespace TEXT NOT NULL UNIQUE,
    is_https BOOLEAN DEFAULT FALSE,
    hosts TEXT[] NOT NULL,

    -- sets then awacs namespace was created
    is_ready BOOLEAN DEFAULT FALSE,

    created_at INTEGER DEFAULT EXTRACT (epoch FROM NOW()),
    updated_at INTEGER DEFAULT NULL,
    deleted_at INTEGER DEFAULT NULL
);

CREATE INDEX balancers_awacs_namespace_idx ON clownductor.balancers(awacs_namespace);

CREATE FUNCTION set_updated() RETURNS trigger AS $set_updated$
    BEGIN
        IF NEW.updated_at IS NULL THEN
            NEW.updated_at = EXTRACT (epoch FROM NOW());
        END IF;
        RETURN NEW;
    END;
$set_updated$ LANGUAGE plpgsql;

CREATE TRIGGER balancers_set_updated BEFORE UPDATE OR INSERT ON clownductor.balancers
    FOR EACH ROW EXECUTE PROCEDURE set_updated();

ALTER TABLE clownductor.branches
    ADD COLUMN balancer_id INTEGER
        REFERENCES clownductor.branches(id);

COMMIT;
