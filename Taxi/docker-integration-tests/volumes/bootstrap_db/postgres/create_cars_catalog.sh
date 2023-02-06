#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE cars_catalog;
\connect cars_catalog

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE SCHEMA cars_catalog;

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

CREATE EXTENSION IF NOT EXISTS amcheck WITH SCHEMA public;

COMMENT ON EXTENSION amcheck IS 'functions for verifying relation integrity';

SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE cars_catalog.brand_models (
    pk bigint NOT NULL,
    revision bigint NOT NULL,
    raw_brand text,
    raw_model text,
    normalized_mark_code text,
    normalized_model_code text,
    corrected_model text
);

CREATE SEQUENCE cars_catalog.brand_models_pk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE cars_catalog.colors (
    pk bigint NOT NULL,
    revision bigint NOT NULL,
    raw_color text NOT NULL,
    normalized_color text NOT NULL,
    color_code text
);

CREATE SEQUENCE cars_catalog.colors_pk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE cars_catalog.meta (
    pk bigint NOT NULL,
    last_updated_ts integer,
    last_inc integer,
    small_task_completed timestamp without time zone,
    large_task_completed timestamp without time zone
);

CREATE SEQUENCE cars_catalog.meta_pk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE cars_catalog.misspells (
    pk bigint NOT NULL,
    raw_value text NOT NULL,
    normalized_value text NOT NULL
);

CREATE SEQUENCE cars_catalog.misspells_pk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE cars_catalog.prices (
    pk bigint NOT NULL,
    revision bigint NOT NULL,
    normalized_mark_code text,
    normalized_model_code text,
    car_year integer,
    car_age integer,
    car_price numeric
);

CREATE SEQUENCE cars_catalog.prices_pk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE cars_catalog.revision_serial_brand_models
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE cars_catalog.revision_serial_colors
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE cars_catalog.revision_serial_prices
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE ONLY cars_catalog.brand_models ALTER COLUMN pk SET DEFAULT nextval('cars_catalog.brand_models_pk_seq'::regclass);

ALTER TABLE ONLY cars_catalog.brand_models ALTER COLUMN revision SET DEFAULT nextval('cars_catalog.revision_serial_brand_models'::regclass);

ALTER TABLE ONLY cars_catalog.colors ALTER COLUMN pk SET DEFAULT nextval('cars_catalog.colors_pk_seq'::regclass);

ALTER TABLE ONLY cars_catalog.colors ALTER COLUMN revision SET DEFAULT nextval('cars_catalog.revision_serial_colors'::regclass);

ALTER TABLE ONLY cars_catalog.meta ALTER COLUMN pk SET DEFAULT nextval('cars_catalog.meta_pk_seq'::regclass);

ALTER TABLE ONLY cars_catalog.misspells ALTER COLUMN pk SET DEFAULT nextval('cars_catalog.misspells_pk_seq'::regclass);

ALTER TABLE ONLY cars_catalog.prices ALTER COLUMN pk SET DEFAULT nextval('cars_catalog.prices_pk_seq'::regclass);

ALTER TABLE ONLY cars_catalog.prices ALTER COLUMN revision SET DEFAULT nextval('cars_catalog.revision_serial_prices'::regclass);

ALTER TABLE ONLY cars_catalog.brand_models
    ADD CONSTRAINT brand_models_pkey PRIMARY KEY (pk);

ALTER TABLE ONLY cars_catalog.colors
    ADD CONSTRAINT colors_pkey PRIMARY KEY (pk);

ALTER TABLE ONLY cars_catalog.colors
    ADD CONSTRAINT colors_raw_color_key UNIQUE (raw_color);

ALTER TABLE ONLY cars_catalog.meta
    ADD CONSTRAINT meta_pkey PRIMARY KEY (pk);

ALTER TABLE ONLY cars_catalog.misspells
    ADD CONSTRAINT misspells_pkey PRIMARY KEY (pk);

ALTER TABLE ONLY cars_catalog.misspells
    ADD CONSTRAINT misspells_raw_value_key UNIQUE (raw_value);

ALTER TABLE ONLY cars_catalog.prices
    ADD CONSTRAINT prices_pkey PRIMARY KEY (pk);

CREATE UNIQUE INDEX brand_car_model_unique ON cars_catalog.brand_models USING btree (raw_brand, raw_model);

CREATE UNIQUE INDEX mark_code_model_code_car_year_unique ON cars_catalog.prices USING btree (normalized_mark_code, normalized_model_code, car_year);

CREATE TABLE cars_catalog.autoru_prices_cache
(
    mark_code  TEXT        NOT NULL,
    model_code TEXT        NOT NULL,
    age        INTEGER     NOT NULL,
    price      NUMERIC     NOT NULL,
    loaded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (mark_code, model_code, age)
);
CREATE INDEX ON cars_catalog.autoru_prices_cache (loaded_at);

CREATE SEQUENCE cars_catalog.revision_serial_prepared_prices;

CREATE TABLE cars_catalog.prepared_prices
(
    revision   BIGINT      NOT NULL DEFAULT NEXTVAL('cars_catalog.revision_serial_prepared_prices'),
    mark_code  TEXT        NOT NULL,
    model_code TEXT        NOT NULL,
    year       INTEGER     NOT NULL,
    price      NUMERIC     NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (mark_code, model_code, year)
);
CREATE INDEX ON cars_catalog.prepared_prices (updated_at);

ALTER SEQUENCE cars_catalog.revision_serial_prepared_prices
    OWNED BY cars_catalog.prepared_prices.revision;

INSERT INTO cars_catalog.colors
    VALUES
        (0, 0, 'Желтый', 'желтый', 'FFD600');

INSERT INTO cars_catalog.brand_models
    VALUES
        (0, 0, 'BMW', '7er', 'BMW', '7ER', 'BMW 7er');

INSERT INTO cars_catalog.prices
    VALUES
        (0, 0, 'BMW', '7ER', 2017, 2017, 4213277);

INSERT INTO cars_catalog.autoru_prices_cache
    (mark_code, model_code, age, price, loaded_at)
    VALUES
        ('BMW', '7ER', 0, '4213277', '2017-06-01+00');

INSERT INTO cars_catalog.prepared_prices
    (mark_code, model_code, year, price)
    VALUES
        ('BMW', '7ER', 2017, '4213277');
