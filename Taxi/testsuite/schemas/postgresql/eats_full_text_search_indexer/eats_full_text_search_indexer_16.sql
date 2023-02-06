BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS fts_indexer.update_retail_place_status (
  place_slug TEXT NOT NULL PRIMARY KEY,
  last_updated_at TIMESTAMPTZ,
  last_error_at TIMESTAMPTZ,
  error TEXT
);

COMMIT TRANSACTION;
