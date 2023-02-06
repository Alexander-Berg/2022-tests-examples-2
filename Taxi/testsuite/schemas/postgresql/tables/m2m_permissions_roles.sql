CREATE TABLE access_control.m2m_permissions_roles
(
    id                 SERIAL      NOT NULL PRIMARY KEY,
    permission_id      INTEGER     NOT NULL REFERENCES access_control.permissions (id) ON DELETE CASCADE,
    role_id            INTEGER     NOT NULL REFERENCES access_control.roles (id) ON DELETE CASCADE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX
    m2m_permissions_roles_permission_role
    ON access_control.m2m_permissions_roles (permission_id, role_id);

CREATE INDEX
    m2m_permissions_roles_role
    ON access_control.m2m_permissions_roles (role_id);
