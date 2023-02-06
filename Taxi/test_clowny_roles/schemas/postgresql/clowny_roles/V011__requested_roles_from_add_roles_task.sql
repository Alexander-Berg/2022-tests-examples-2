CREATE TABLE meta.requested_roles (
    idm_role_id BIGINT NOT NULL UNIQUE,

    role_slug TEXT NOT NULL,
    -- scope node (clownductor entity id), to which this role belongs
    external_ref_slug TEXT NOT NULL,
    ref_type roles.ref_type_e NOT NULL,

    login TEXT,
    group_id INTEGER
);

ALTER TABLE meta.requested_roles
    ADD CONSTRAINT requested_roles_ownerless_role CHECK ( NOT (login IS NULL AND group_id IS NULL) )
;
