CREATE SCHEMA surge;

CREATE TABLE surge.calculated
(
    created    TIMESTAMPTZ NOT NULL,
    depot_id   TEXT NOT NULL,
    pipeline   TEXT NOT NULL,
    load_level DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (created, depot_id, pipeline)
);
