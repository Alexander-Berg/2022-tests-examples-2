BEGIN;

ALTER TABLE eats_picker_item_categories.categories ADD COLUMN IF NOT EXISTS public_parent_id TEXT;

CREATE TYPE eats_picker_item_categories.categories_v2 AS (
    id BIGINT,
    public_id TEXT,
    name TEXT,
    public_parent_id TEXT
);

ALTER TABLE eats_picker_item_categories.item_categories ADD COLUMN IF NOT EXISTS level INTEGER;
ALTER TABLE eats_picker_item_categories.item_categories ADD COLUMN IF NOT EXISTS hierarchy_number INTEGER;

CREATE TYPE eats_picker_item_categories.item_categories_v2 AS (
    item_id BIGINT,
    category_id BIGINT,
    level INTEGER,
    hierarchy_number INTEGER
);

CREATE INDEX ix_eats_picker_item_categories_items_eats_item_id
    ON eats_picker_item_categories.items (eats_item_id);
CREATE INDEX ix_eats_picker_item_categories_item_categories_hierarchy_number
    ON eats_picker_item_categories.item_categories (hierarchy_number);
CREATE INDEX ix_eats_picker_item_categories_item_categories_level
    ON eats_picker_item_categories.item_categories (level);

COMMIT;
