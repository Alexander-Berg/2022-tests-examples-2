-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

CREATE SCHEMA voice_gateways;

CREATE TYPE voice_gateways.info_t AS (
  host TEXT,
  ignore_certificate BOOLEAN
);

CREATE TYPE voice_gateways.settings_t AS (
  weight INTEGER,
  disabled BOOLEAN,
  name TEXT,
  idle_expires_in INTEGER
);

CREATE TABLE voice_gateways.voice_gateways(
  id TEXT NOT NULL UNIQUE,
  enabled_at timestamptz,
  disabled_at timestamptz,
  info voice_gateways.info_t NOT NULL,
  settings voice_gateways.settings_t NOT NULL,
  token TEXT NOT NULL,
  deleted BOOLEAN NOT NULL DEFAULT FALSE,
  disable_reason TEXT,
  enable_after timestamptz,
  relapse_count INTEGER,
  PRIMARY KEY(id)
);

CREATE TABLE voice_gateways.disabling_history(
  id BIGSERIAL PRIMARY KEY,
  voice_gateway_id TEXT NOT NULL,
  enabled_at timestamptz,
  disabled_at timestamptz NOT NULL DEFAULT current_timestamp,
  disable_reason TEXT NOT NULL,
  additional_disable_data JSONB,
  additional_enable_data JSONB,
  disabled_by TEXT,
  enabled_by TEXT,
  enable_after timestamptz,
  relapse_count INTEGER
);

CREATE INDEX voice_gateways_disabling_history_voice_gateway_id
    ON voice_gateways.disabling_history(voice_gateway_id);

CREATE FUNCTION voice_gateways.status_changed() RETURNS TRIGGER
  AS $$
BEGIN
  IF TG_OP = 'UPDATE' THEN
    IF (NEW.settings).disabled = (OLD.settings).disabled THEN
      RETURN NEW;
    END IF;
  END IF;

  IF (NEW.settings).disabled THEN
    NEW.disabled_at := current_timestamp;
  ELSE
    NEW.enabled_at := current_timestamp;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER status_changed_tr
BEFORE INSERT OR UPDATE OF settings ON voice_gateways.voice_gateways
FOR EACH ROW
EXECUTE PROCEDURE voice_gateways.status_changed();
