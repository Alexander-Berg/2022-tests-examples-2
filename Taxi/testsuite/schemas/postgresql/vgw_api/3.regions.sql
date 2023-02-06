-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

CREATE SCHEMA regions;

CREATE TYPE regions.consumer_settings_t AS (
  consumer_id INTEGER,
  enabled BOOLEAN
);

CREATE TYPE regions.settings_v2_t AS (
  gateway_id TEXT,
  enabled BOOLEAN,
  city_id TEXT,
  enabled_for common.client_type_t[],
  consumers regions.consumer_settings_t[]
);

CREATE TYPE regions.region_v2_t AS (
  region_id INTEGER,
  gateways regions.settings_v2_t[]
);

CREATE TYPE regions.settings_t AS (
  gateway_id TEXT,
  enabled BOOLEAN,
  city_id TEXT,
  enabled_for common.client_type_t[]
);

CREATE TYPE regions.region_t AS (
  region_id INTEGER,
  gateways regions.settings_t[]
);

CREATE TABLE regions.regions(
  id INTEGER PRIMARY KEY,
  deleted BOOLEAN NOT NULL DEFAULT FALSE,
  updated_at timestamptz NOT NULL DEFAULT current_timestamp
);

CREATE INDEX regions_updated_idx ON regions.regions (updated_at);

CREATE TABLE regions.gateway_region_settings(
  region_id INTEGER NOT NULL REFERENCES regions.regions(id) ON DELETE CASCADE,
  gateway_id TEXT NOT NULL REFERENCES voice_gateways.voice_gateways(id) ON DELETE CASCADE,
  enabled BOOLEAN NOT NULL DEFAULT FALSE,  -- to be deleted
  city_id TEXT NOT NULL,
  enabled_for common.client_type_t[],
  PRIMARY KEY (region_id, gateway_id)
);

CREATE TABLE regions.vgw_enable_settings(
  region_id INTEGER NOT NULL REFERENCES regions.regions(id) ON DELETE CASCADE,
  gateway_id TEXT NOT NULL REFERENCES voice_gateways.voice_gateways(id) ON DELETE CASCADE,
  consumer_id INTEGER NOT NULL REFERENCES consumers.consumers(id) ON DELETE CASCADE,
  enabled BOOLEAN NOT NULL,
  updated_at timestamptz DEFAULT current_timestamp,
  PRIMARY KEY (gateway_id, region_id, consumer_id)
);

CREATE FUNCTION regions.updated() RETURNS TRIGGER
AS $$
BEGIN
  IF tg_table_name = 'gateway_region_settings' THEN
    UPDATE regions.regions SET updated_at = default
    WHERE id = NEW.region_id;
  END IF;
  IF tg_table_name = 'vgw_enable_settings' THEN
      UPDATE regions.regions SET updated_at = default
      WHERE id = NEW.region_id;
  END IF;
  IF tg_table_name = 'regions' THEN
    NEW.updated_at := current_timestamp;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER regions_settings_updated_tr
  BEFORE INSERT OR UPDATE ON regions.gateway_region_settings
  FOR EACH ROW
EXECUTE PROCEDURE regions.updated();

CREATE TRIGGER vgw_enable_settings_updated_tr
    BEFORE INSERT OR UPDATE ON regions.vgw_enable_settings
    FOR EACH ROW
EXECUTE PROCEDURE regions.updated();

CREATE TRIGGER regions_updated_tr
  BEFORE UPDATE OF deleted ON regions.regions
  FOR EACH ROW
EXECUTE PROCEDURE regions.updated();
