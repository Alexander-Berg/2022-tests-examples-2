BEGIN;

CREATE SCHEMA eats_picker_item_categories;

CREATE TABLE eats_picker_item_categories.items (
    id BIGSERIAL PRIMARY KEY,
    place_id INTEGER NOT NULL,
    eats_item_id TEXT NOT NULL,
    synchronized_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX ix_eats_picker_item_categories_items_place_id_eats_item_id
ON eats_picker_item_categories.items (place_id, eats_item_id);

CREATE TYPE eats_picker_item_categories.items_v1 AS(
    id BIGINT,
    place_id INTEGER,
    eats_item_id TEXT,
    synchronized_at TIMESTAMPTZ 
);

CREATE TABLE eats_picker_item_categories.categories (
    id BIGSERIAL PRIMARY KEY,
    public_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);

CREATE TYPE eats_picker_item_categories.categories_v1 AS (
    id BIGINT,
    public_id TEXT,
    name TEXT
);

CREATE TABLE eats_picker_item_categories.item_categories (
    item_id BIGINT REFERENCES eats_picker_item_categories.items (id),
    category_id BIGINT REFERENCES eats_picker_item_categories.categories (id),
    PRIMARY KEY (item_id, category_id)
);

CREATE TYPE eats_picker_item_categories.item_categories_v1 AS (
    item_id BIGINT,
    category_id BIGINT
);

COMMIT;
