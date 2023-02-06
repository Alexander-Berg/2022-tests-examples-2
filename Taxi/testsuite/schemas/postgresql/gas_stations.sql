CREATE SCHEMA gas_stations;

CREATE TABLE gas_stations.partner_contracts_acceptance
(
  park_id     VARCHAR(255)    NOT NULL,
  clid        VARCHAR(255)    NOT NULL UNIQUE,
  started     TIMESTAMPTZ     NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
  finished    TIMESTAMPTZ     NULL,
  created     TIMESTAMPTZ     NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'), 
  updated     TIMESTAMPTZ     NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
  PRIMARY KEY (park_id)
);

CREATE UNIQUE INDEX partner_contracts_acceptance_by_clid_idx
ON gas_stations.partner_contracts_acceptance(clid);

CREATE OR REPLACE FUNCTION trigger_set_updated()
    RETURNS TRIGGER AS $$
BEGIN
    NEW.updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_timestamp
    BEFORE UPDATE ON gas_stations.partner_contracts_acceptance
    FOR EACH ROW
EXECUTE PROCEDURE trigger_set_updated();


CREATE OR REPLACE FUNCTION trigger_remove_finished()
    RETURNS TRIGGER AS $$
BEGIN
    NEW.finished = NULL;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER remove_finished_on_start
    BEFORE UPDATE OF started ON gas_stations.partner_contracts_acceptance
    FOR EACH ROW
EXECUTE PROCEDURE trigger_remove_finished();

CREATE TABLE gas_stations.distlock
(
    key             TEXT PRIMARY KEY,
    owner           TEXT,
    expiration_time TIMESTAMPTZ
);
