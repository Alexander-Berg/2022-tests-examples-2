CREATE SCHEMA meta;

CREATE TYPE meta.role_ownership_e AS ENUM (
    'personal', 'group'
);

CREATE TYPE meta_role_state_e AS ENUM (
    'approved',
    'created',
    'declined',
    'deprived',
    'depriving',
    'expired',
    'failed',
    'granted',
    'need_request',
    'requested',
    'rerequested',
    'review_request'
);

CREATE TABLE meta.checked_roles (
    role_id BIGINT PRIMARY KEY,
    checked_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_state meta_role_state_e NOT NULL,
    ownership meta.role_ownership_e NOT NULL
);
