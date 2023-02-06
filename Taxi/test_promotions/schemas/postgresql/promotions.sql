SET default_text_search_config = 'pg_catalog.russian';

CREATE SCHEMA IF NOT EXISTS promotions;

CREATE TABLE promotions.promotions(
    id TEXT PRIMARY KEY,
    revision TEXT,
    revision_history jsonb,
    name TEXT UNIQUE NOT NULL,
    name_tsv tsvector NOT NULL,
    promotion_type TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'created',
    meta_tags TEXT[],
    zones TEXT[] NOT NULL,
    screens TEXT[] NOT NULL,
    consumers TEXT[],
    priority INTEGER DEFAULT 1,
    starts_at TIMESTAMPTZ,
    ends_at TIMESTAMPTZ,
    experiment TEXT,
    has_yql_data BOOLEAN NOT NULL DEFAULT FALSE,
    yql_data jsonb,
    pages jsonb NOT NULL,
    extra_fields jsonb
);

CREATE INDEX promotions_id_revision_idx ON promotions.promotions (id, revision) WHERE revision NOTNULL;
CREATE INDEX promotions_experiment_idx ON promotions.promotions USING hash(experiment);
CREATE INDEX promotions_name_tsv_gin_idx ON promotions.promotions USING gin(name_tsv);
CREATE INDEX promotions_experiment_starts_ends_cond_btree_idx ON promotions.promotions
    USING btree (experiment, starts_at, ends_at DESC) WHERE status = 'published' AND experiment NOTNULL;
CREATE INDEX promotions_starts_at_ends_at_cond_btree_idx ON promotions.promotions
    USING btree (starts_at, ends_at DESC) WHERE status = 'published' AND has_yql_data IS TRUE;
CREATE INDEX promotions_has_yql_data_idx ON promotions.promotions(has_yql_data) WHERE has_yql_data IS TRUE;
CREATE INDEX promotions_has_yql_data_stopped_ends_at_idx ON promotions.promotions
    USING btree (status, ends_at DESC) WHERE has_yql_data IS TRUE;
CREATE INDEX promotions_type_status_created_at_btree_idx
    ON promotions.promotions USING btree (promotion_type, status, created_at DESC)
    WHERE status = 'published' AND promotion_type = 'story';
CREATE INDEX promotions_consumers_gin_idx ON promotions.promotions
    USING gin(consumers) WHERE consumers NOTNULL;
CREATE INDEX promotions_meta_tags_gin_idx ON promotions.promotions
    USING gin(meta_tags) WHERE meta_tags NOTNULL;
CREATE INDEX promotions_extra_fields_gin_ids ON promotions.promotions
    USING gin(extra_fields);

CREATE TABLE promotions.yql_cache(
    promotion_id TEXT NOT NULL REFERENCES promotions.promotions,
    yandex_uid TEXT,
    user_id TEXT,
    phone_id TEXT,
    data jsonb NOT NULL
);
CREATE INDEX yql_cache_promotion_id_yandex_uid ON promotions.yql_cache(promotion_id, yandex_uid);
CREATE INDEX yql_cache_promotion_id_user_id ON promotions.yql_cache(promotion_id, user_id);
CREATE INDEX yql_cache_promotion_id_phone_id ON promotions.yql_cache(promotion_id, phone_id);

CREATE TABLE promotions.media_tags(
    id TEXT PRIMARY KEY,
    "type" TEXT NOT NULL,
    resize_mode TEXT NOT NULL,
    sizes jsonb NOT NULL
);

CREATE TABLE promotions.promo_on_map(
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    name_tsv tsvector NOT NULL,
    priority INTEGER DEFAULT 1,
    image_tag TEXT NOT NULL,
    action jsonb NOT NULL,
    bubble jsonb NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'created',
    starts_at TIMESTAMPTZ,
    ends_at TIMESTAMPTZ,
    experiment TEXT,
    cache_distance INTEGER NOT NULL,
    attract_to_road BOOLEAN NOT NULL DEFAULT FALSE,
    campaign_labels TEXT[]
);
CREATE INDEX promo_on_map_created_at_status ON promotions.promo_on_map USING btree(updated_at, status);
CREATE INDEX promo_on_map_status_published ON promotions.promo_on_map USING hash(status) WHERE status = 'published';
CREATE INDEX promo_on_map_name_tsv_gin ON promotions.promo_on_map USING gin(name_tsv);

CREATE SEQUENCE promotions.eda_banner_id_seq;

CREATE TABLE promotions.collections(
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    name_tsv tsvector NOT NULL,
    cells jsonb NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX collections_name_tsv_gin ON promotions.collections USING gin(name_tsv);

CREATE TABLE promotions.showcases(
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    name_tsv tsvector NOT NULL,
    collection_blocks jsonb NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'created',
    screens TEXT[] NOT NULL DEFAULT '{}'::TEXT[],
    starts_at TIMESTAMPTZ,
    ends_at TIMESTAMPTZ,
    experiment TEXT
);
CREATE INDEX showcases_name_tsv_gin ON promotions.showcases USING gin(name_tsv);

CREATE TABLE promotions.campaigns(
    campaign_label TEXT PRIMARY KEY,
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_test_publication BOOLEAN NOT NULL DEFAULT FALSE
);
