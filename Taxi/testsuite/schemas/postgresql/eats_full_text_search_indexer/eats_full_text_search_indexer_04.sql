BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS fts_indexer.document_meta (
  prefix INTEGER,                                 -- prefix (kps) в saas
  url TEXT,                                       -- url документа (идентификатор в saas)
  hash TEXT NOT NULL,                             -- hash документа
  place_slug TEXT NOT NULL,                       -- slug заведения
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- время обновления
  PRIMARY KEY (prefix, url)
);

CREATE INDEX idx__document_meta__updated_at ON fts_indexer.document_meta(updated_at);

CREATE TYPE fts_indexer.document_meta_v1 AS (
  prefix INTEGER,
  url TEXT,
  hash TEXT,
  place_slug TEXT
);

COMMIT TRANSACTION;
