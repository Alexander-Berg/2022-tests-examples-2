CREATE TABLE roles.grands (
    id BIGSERIAL PRIMARY KEY,
    login TEXT NOT NULL,
    role_id BIGINT REFERENCES roles.roles(id) ON DELETE RESTRICT NOT NULL,

    is_fired BOOLEAN,

    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,

    CONSTRAINT deleted_with_set_fired_flag CHECK
        ( is_deleted <> ( is_fired IS NULL) )
);
CREATE UNIQUE INDEX roles_grands_uniq_key_idx
    ON roles.grands(login, role_id)
    WHERE NOT is_deleted;
CREATE TRIGGER roles_grands_set_updated
    BEFORE UPDATE OR INSERT ON roles.grands
    FOR EACH ROW EXECUTE PROCEDURE roles.set_updated();
CREATE TRIGGER roles_grands_set_deleted
    BEFORE UPDATE ON roles.grands
    FOR EACH ROW EXECUTE PROCEDURE roles.set_deleted();

CREATE TYPE roles.grand_v1 AS (
    id BIGINT,
    login TEXT,
    role_id BIGINT,

    is_fired BOOLEAN,

    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    is_deleted BOOLEAN
);
