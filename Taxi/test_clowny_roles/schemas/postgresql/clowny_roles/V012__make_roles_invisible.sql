ALTER TABLE roles.roles ADD COLUMN visible BOOLEAN DEFAULT TRUE;
ALTER TABLE roles.registered_roles ADD COLUMN visible BOOLEAN DEFAULT TRUE;

CREATE TYPE roles.role_v2 AS (
    id BIGINT,
    slug TEXT,
    fields jsonb,

    name roles.translatable_t,
    help roles.translatable_t,

    external_ref_slug TEXT,
    ref_type roles.ref_type_e,
    visible BOOLEAN,

    subsystem_id BIGINT,

    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    is_deleted BOOLEAN
);
