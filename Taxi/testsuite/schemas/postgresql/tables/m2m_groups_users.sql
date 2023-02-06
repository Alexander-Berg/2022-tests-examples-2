CREATE TABLE access_control.m2m_groups_users
(
    id                 SERIAL      NOT NULL PRIMARY KEY,
    group_id           INTEGER     NOT NULL REFERENCES access_control.groups (id) ON DELETE CASCADE,
    user_id            INTEGER     NOT NULL REFERENCES access_control.users (id) ON DELETE CASCADE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX
    m2m_groups_users_group_user
    ON access_control.m2m_groups_users (group_id, user_id);

CREATE INDEX
    m2m_groups_users_user_id
    ON access_control.m2m_groups_users (user_id);
