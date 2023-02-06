CREATE SCHEMA IF NOT EXISTS cargo_pricing;

--calculations
CREATE TABLE IF NOT EXISTS cargo_pricing.calculations
(
    id                   UUID           NOT NULL PRIMARY KEY,
    shared_parts_hashes  TEXT[]
);

CREATE INDEX IF NOT EXISTS idx__calculations__shared_parts_hashes ON cargo_pricing.calculations
    USING GIN (shared_parts_hashes) WITH (FASTUPDATE=OFF);

--shared_calcs_parts
CREATE TABLE IF NOT EXISTS cargo_pricing.shared_calcs_parts
(
    id                   UUID           NOT NULL PRIMARY KEY,
    hash                 TEXT           NOT NULL,
    updated_ts           TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS
  idx__shared_calcs_parts__hash
ON
  cargo_pricing.shared_calcs_parts(hash);

CREATE INDEX IF NOT EXISTS
    idx__shared_calcs_parts__updated_ts
    ON cargo_pricing.shared_calcs_parts(updated_ts);
