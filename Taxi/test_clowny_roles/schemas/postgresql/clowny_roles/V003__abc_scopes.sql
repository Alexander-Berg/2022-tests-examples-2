CREATE TABLE roles.abc_scopes (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    -- https://wiki.yandex-team.ru/intranet/idm/API/#node-params
    name roles.translatable_t NOT NULL,
    help roles.translatable_t NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP DEFAULT NULL,
    is_deleted BOOLEAN DEFAULT FALSE
);
