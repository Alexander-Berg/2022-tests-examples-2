CREATE SCHEMA IF NOT EXISTS eats_retail_categories;

CREATE TABLE IF NOT EXISTS eats_retail_categories.user_orders_updates_log
(
    eater_id   TEXT PRIMARY KEY,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS eats_retail_categories.brands
(
    id            BIGINT      NOT NULL PRIMARY KEY,
    slug          TEXT        NOT NULL,
    picture_scale TEXT,
    is_enabled    BOOLEAN     NOT NULL DEFAULT FALSE,
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO eats_retail_categories.brands (id, slug, picture_scale, is_enabled, updated_at)
VALUES (100828, 'polon_lenta_integration', 'aspect_fill', true, '2022-05-23 11:36:02.289468 +00:00'::timestamptz);

CREATE TABLE IF NOT EXISTS eats_retail_categories.user_ordered_products
(
    eater_id     TEXT        NOT NULL,
    brand_id     BIGINT      NOT NULL REFERENCES eats_retail_categories.brands (id),
    public_id    TEXT        NOT NULL,
    orders_count INT         NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (eater_id, brand_id, public_id)
);

CREATE TABLE IF NOT EXISTS eats_retail_categories.user_cross_brand_ordered_products
(
    eater_id     TEXT        NOT NULL,
    sku_id       TEXT        NOT NULL,
    orders_count INT         NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (eater_id, sku_id)
);
