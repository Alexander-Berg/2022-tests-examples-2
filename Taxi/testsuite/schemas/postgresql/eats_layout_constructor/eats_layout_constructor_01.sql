BEGIN TRANSACTION;

CREATE SCHEMA constructor;

CREATE TABLE constructor.meta_widgets (
  id BIGSERIAL PRIMARY KEY,
  type TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  settings JSONB NOT NULL,
  created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE constructor.widget_templates (
    id BIGSERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    meta JSONB NOT NULL,
    payload JSONB NOT NULL,
    payload_schema JSONB NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE constructor.layouts (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    author TEXT NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE constructor.layout_widgets (
    id BIGSERIAL PRIMARY KEY,  -- идентификатор записи, при пересохранении layout'a все записи создаются заново
    url_id BIGSERIAL NOT NULL,  -- идентифиактор для создания ссылки, копируется в новую запись при пересохранении layout'a
    name TEXT NOT NULL,
    widget_template_id BIGSERIAL NOT NULL REFERENCES constructor.widget_templates(id) ON DELETE RESTRICT,
    layout_id BIGSERIAL NOT NULL REFERENCES constructor.layouts(id),
    meta JSONB NOT NULL,
    payload JSONB NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TYPE constructor.layout_widget_v1 AS (
    url_id INTEGER,
    widget_template_id INTEGER,
    name TEXT,
    type TEXT,
    template_meta JSONB,
    meta JSONB,
    payload_schema JSONB,
    template_payload JSONB,
    payload JSONB
);

COMMIT TRANSACTION;
