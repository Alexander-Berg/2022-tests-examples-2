BEGIN TRANSACTION;

DROP TABLE IF EXISTS fts.categories_mapping CASCADE;

DROP INDEX IF EXISTS fts.idx__items_mapping__updated_at;

COMMIT TRANSACTION;
