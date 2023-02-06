CREATE SCHEMA auto_merge;

CREATE TABLE auto_merge.viewed_pulls (
    number BIGINT PRIMARY KEY,
    ref TEXT NOT NULL,

    mergeable_by_devs BOOLEAN NOT NULL,
    is_solomon_only BOOLEAN NOT NULL,
    responsibles TEXT[] NOT NULL
);
