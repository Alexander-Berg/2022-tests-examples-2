CREATE SCHEMA caches;

CREATE TYPE caches.found_item_t AS (
    real_name TEXT,
    lang TEXT,
    region_id INTEGER
);

CREATE TABLE caches.geodata_regions (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER REFERENCES caches.geodata_regions(id),
    country_id INTEGER REFERENCES caches.geodata_regions(id),
    population INTEGER NOT NULL,
    region_type INTEGER NOT NULL,
    last_updated_ts INTEGER NOT NULL
);

CREATE TABLE caches.geodata_localized_names (
    real_name TEXT NOT NULL,
    lower_name TEXT NOT NULL,
    lang TEXT NOT NULL,
    region_id INTEGER REFERENCES caches.geodata_regions(id) ON DELETE RESTRICT NOT NULL,

    UNIQUE (region_id, lang)
);

CREATE INDEX caches_geodata_localized_names_region_id_lang_idx
    ON caches.geodata_localized_names(region_id, lang);
