CREATE SCHEMA IF NOT EXISTS snb_eda;

CREATE TABLE snb_eda.rad_suggests (
    place_id bigint,
    suggest text,
    prioriy numeric
);
