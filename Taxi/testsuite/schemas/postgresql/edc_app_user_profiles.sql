CREATE SCHEMA IF NOT EXISTS edc_app_user_profiles;

SET SEARCH_PATH TO edc_app_user_profiles;

CREATE TABLE IF NOT EXISTS edc_app_user_profiles.user_profiles(
  id uuid NOT NULL PRIMARY KEY,
  organization_id uuid NOT NULL,
  first_name TEXT NOT NULL,
  middle_name TEXT NULL,
  last_name TEXT NOT NULL,
  phone_pd_id TEXT NULL,
  yandex_uid TEXT NULL,
  is_dispatcher BOOLEAN NOT NULL,
  updated_ts TIMESTAMPTZ NOT NULL,
  UNIQUE (organization_id, phone_pd_id),
  UNIQUE (organization_id, yandex_uid)
);

CREATE TABLE IF NOT EXISTS edc_app_user_profiles.physician_details(
  id uuid NOT NULL PRIMARY KEY,
  user_id uuid NOT NULL UNIQUE,
  updated_ts TIMESTAMPTZ NOT NULL,
  FOREIGN KEY(user_id)
    REFERENCES edc_app_user_profiles.user_profiles(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE TABLE IF NOT EXISTS edc_app_user_profiles.technician_details(
  id uuid NOT NULL PRIMARY KEY,
  user_id uuid NOT NULL UNIQUE,
  diploma TEXT NOT NULL,
  updated_ts TIMESTAMPTZ NOT NULL,
  FOREIGN KEY(user_id)
    REFERENCES edc_app_user_profiles.user_profiles(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE TABLE IF NOT EXISTS edc_app_user_profiles.driver_details(
  id uuid NOT NULL PRIMARY KEY,
  user_id uuid NOT NULL UNIQUE,
  license_pd_id TEXT NOT NULL,
  sex TEXT NOT NULL,
  birth_date TIMESTAMP NOT NULL,
  vehicle_id uuid NULL,
  updated_ts TIMESTAMPTZ NOT NULL,
  FOREIGN KEY(user_id)
    REFERENCES edc_app_user_profiles.user_profiles(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE INDEX IF NOT EXISTS user_profiles_full_name_idx 
    ON edc_app_user_profiles.user_profiles(last_name, first_name, middle_name);
