CREATE TABLE access_control.m2m_groups_roles
(
    id                 SERIAL      NOT NULL PRIMARY KEY,
    group_id           INTEGER     NOT NULL REFERENCES access_control.groups (id) ON DELETE CASCADE,
    role_id            INTEGER     NOT NULL REFERENCES access_control.roles (id) ON DELETE CASCADE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX
    m2m_groups_roles_group_role
    ON access_control.m2m_groups_roles (group_id, role_id);
