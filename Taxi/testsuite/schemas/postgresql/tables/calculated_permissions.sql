CREATE TYPE access_control.calculated_permissions_t_v1 AS
(
    rule_name          TEXT,
    rule_storage       access_control.storage_t,
    rule_path          TEXT,
    rule_value         TEXT
);

CREATE TABLE access_control.calculated_permissions
(
    id                 SERIAL      NOT NULL PRIMARY KEY,
    role_id            INTEGER     NOT NULL REFERENCES access_control.roles (id) ON DELETE CASCADE,
    rule_id            INTEGER     NOT NULL REFERENCES access_control.permission_calculation_rules (id) ON DELETE CASCADE,
    rule_value         TEXT        NOT NULL,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX
    calculated_permissions_rule_id_name
ON
    access_control.calculated_permissions (
         rule_id,
         rule_value
    );

CREATE INDEX
    calculated_permissions_role_id
ON
    access_control.calculated_permissions (role_id);
