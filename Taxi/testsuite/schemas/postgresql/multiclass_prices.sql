\set ON_ERROR_STOP on

/* v1 */
CREATE schema multiclass;

CREATE TABLE info(
    id TEXT NOT NULL UNIQUE,
    doc jsonb NOT NULL,
    due timestamp NOT NULL
);

CREATE TABLE distlock(
    key TEXT PRIMARY KEY,
    owner TEXT,
    expiration_time TIMESTAMPTZ
);
