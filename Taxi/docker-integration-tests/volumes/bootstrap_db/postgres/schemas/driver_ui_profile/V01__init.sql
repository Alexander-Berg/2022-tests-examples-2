CREATE SCHEMA IF NOT EXISTS state;

CREATE TABLE IF NOT EXISTS state.drivers (
    id serial PRIMARY KEY,
    park_id text NOT NULL,
    driver_profile_id text NOT NULL,
    UNIQUE (park_id, driver_profile_id)
);

CREATE TABLE IF NOT EXISTS state.display_modes (
    id serial PRIMARY KEY,
    name text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS state.display_profiles (
    id serial PRIMARY KEY,
    name text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS state.profiles (
    driver_id int PRIMARY KEY REFERENCES state.drivers (id),
    display_mode_id int NOT NULL REFERENCES state.display_modes (id),
    display_profile_id int NOT NULL REFERENCES state.display_profiles (id),
    updated timestamptz NOT NULL DEFAULT NOW()
);
