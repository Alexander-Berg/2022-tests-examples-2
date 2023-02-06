CREATE SCHEMA eats_order_revision;

-- revisions
CREATE TABLE IF NOT EXISTS eats_order_revision.revisions (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- revision_tags
CREATE TABLE IF NOT EXISTS eats_order_revision.revision_tags (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    revision_id BIGSERIAL NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- revision_mixins
CREATE TABLE IF NOT EXISTS eats_order_revision.revision_mixins (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    order_id TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE eats_order_revision.revision_tags
    ADD CONSTRAINT fkey__revision_tags__revision_id  FOREIGN KEY (revision_id)
        REFERENCES eats_order_revision.revisions(id) ON DELETE CASCADE;
