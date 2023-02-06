DROP INDEX roles.roles_registered_non_deleted;

CREATE UNIQUE INDEX roles_registered_unique_slug
    ON roles.registered_roles(slug) WHERE NOT is_deleted;
