BEGIN;

CREATE INDEX IF NOT EXISTS ix_eats_picker_item_categories_synchronized_at
ON eats_picker_item_categories.items(synchronized_at);

COMMIT;
