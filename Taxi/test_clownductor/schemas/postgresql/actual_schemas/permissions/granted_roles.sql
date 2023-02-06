CREATE TABLE permissions.granted_roles (
    idm_id BIGINT NOT NULL UNIQUE,
    service_id BIGINT NOT NULL REFERENCES clownductor.services(id),
    process_name TEXT NOT NULL
);
