CREATE SCHEMA IF NOT EXISTS fleet_sync;

CREATE TABLE IF NOT EXISTS fleet_sync.parks_mappings (
   park_id varchar(32) NOT NULL,
   mapped_park_id varchar(32) NOT NULL,
   app_family varchar(32) NOT NULL,
   created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (mapped_park_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS parks_to_mapped ON fleet_sync.parks_mappings (park_id, app_family);


CREATE TABLE IF NOT EXISTS fleet_sync.drivers_mappings (
   park_id varchar(32) NOT NULL,
   driver_id varchar(32) NOT NULL,
   mapped_driver_id varchar(32) NOT NULL,
   app_family varchar(32) NOT NULL,
   created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (park_id, mapped_driver_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS drivers_to_mapped ON fleet_sync.drivers_mappings (park_id, driver_id, app_family);


CREATE TABLE IF NOT EXISTS fleet_sync.cars_mappings (
   park_id varchar(32) NOT NULL,
   car_id varchar(32) NOT NULL,
   mapped_car_id varchar(32) NOT NULL,
   app_family varchar(32) NOT NULL,
   created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (park_id, mapped_car_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS cars_to_mapped ON fleet_sync.cars_mappings (park_id, car_id, app_family);

CREATE SCHEMA IF NOT EXISTS auxiliary;

CREATE TABLE IF NOT EXISTS auxiliary.cursors (
   app_family varchar(32) NOT NULL,
   task_type varchar(32) NOT NULL,
   last_updated_ts varchar(64) NOT NULL,
   PRIMARY KEY (app_family, task_type)
);

CREATE TABLE IF NOT EXISTS auxiliary.distlocks(
  key varchar(256) NOT NULL,
  owner TEXT NOT NULL,
  expiration_time TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (key)
);
