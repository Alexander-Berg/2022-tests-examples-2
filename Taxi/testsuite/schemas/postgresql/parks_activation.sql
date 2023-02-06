-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

DROP SCHEMA IF EXISTS parks_activation CASCADE;

CREATE SCHEMA parks_activation;

CREATE TYPE parks_activation.recommended_payment_t AS (
  contract_id INTEGER,
  recommended_payment FLOAT
);

CREATE TABLE parks_activation.accounts(
  park_id TEXT PRIMARY KEY,
  city_id TEXT NOT NULL,
  promised_payment_till TIMESTAMPTZ,
  threshold FLOAT,
  dynamic_threshold FLOAT,
  recommended_payments parks_activation.recommended_payment_t[] NOT NULL
  DEFAULT '{}'::parks_activation.recommended_payment_t[],
  contracts_revision INTEGER,
  balances_revision INTEGER,
  skipped BOOLEAN NOT NULL DEFAULT FALSE,
  skipped_reason TEXT,
  mongo_revision TEXT NOT NULL,
  require_card BOOLEAN,
  require_coupon BOOLEAN,
  has_corp_vat BOOLEAN NOT NULL DEFAULT FALSE,
  current_corp_vat INTEGER
);

CREATE TABLE parks_activation.parks(
   park_id TEXT PRIMARY KEY REFERENCES parks_activation.accounts (park_id) ON DELETE CASCADE,
   deactivated BOOLEAN NOT NULL DEFAULT FALSE,
   deactivated_reason TEXT,
   can_cash BOOLEAN NOT NULL DEFAULT FALSE,
   can_card  BOOLEAN NOT NULL DEFAULT FALSE,
   can_coupon  BOOLEAN NOT NULL DEFAULT FALSE,
   can_corp  BOOLEAN NOT NULL DEFAULT FALSE,
   has_corp_without_vat_contract BOOLEAN NOT NULL DEFAULT FALSE,
   can_corp_without_vat BOOLEAN NOT NULL DEFAULT FALSE,
   can_subsidy  BOOLEAN NOT NULL DEFAULT FALSE,
   can_card_reason TEXT DEFAULT NULL,
   can_cash_reason TEXT DEFAULT NULL,
   can_corp_reason TEXT DEFAULT NULL,
   can_corp_without_vat_reason TEXT DEFAULT NULL,
   can_coupon_reason TEXT DEFAULT NULL,
   can_subsidy_reason TEXT DEFAULT NULL,
   updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
   revision BIGSERIAL,
   can_logistic BOOLEAN NOT NULL DEFAULT FALSE,
   can_logistic_reason TEXT DEFAULT NULL
);

CREATE INDEX parks_activation_accounts_updated_revision
ON parks_activation.parks(
  updated, revision
);

CREATE TYPE parks_activation.balance_t AS (
  contract_id INTEGER,
  balance FLOAT
);

CREATE TABLE parks_activation.change_history(
  id BIGSERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  park_id TEXT NOT NULL,
  field_name TEXT NOT NULL,
  /* We're not interested in types here */
  before TEXT,
  after TEXT
);

CREATE INDEX parks_activation_change_history_park_id_timestamp
ON parks_activation.change_history(
  park_id, timestamp
);

CREATE TABLE parks_activation.last_mongo_revision(
  name TEXT PRIMARY KEY,
  last_mongo_revision TEXT NOT NULL DEFAULT '0_0'
);

DROP SCHEMA IF EXISTS distlocks CASCADE;
CREATE SCHEMA distlocks;

CREATE TABLE distlocks.parks_activation_locks(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);

CREATE TABLE parks_activation.activation_queue(
  park_id TEXT NOT NULL PRIMARY KEY REFERENCES parks_activation.accounts (park_id) ON DELETE CASCADE,
  last_task_run TIMESTAMPTZ NOT NULL DEFAULT TO_TIMESTAMP(0),
  fails INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX parks_activation_activation_queue_park_id_last_try
ON parks_activation.activation_queue(
   park_id, last_task_run
);

CREATE FUNCTION parks_activation.park_inserted() RETURNS TRIGGER
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO parks_activation.activation_queue (park_id)
        VALUES (NEW.park_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER new_park_inserted
    AFTER INSERT ON parks_activation.accounts
    FOR EACH ROW
EXECUTE PROCEDURE parks_activation.park_inserted();

ALTER TABLE parks_activation.change_history
ADD COLUMN reason TEXT,
ADD COLUMN additional_data TEXT;

-- separate logistics and taxi

ALTER TABLE parks_activation.parks
    ADD COLUMN IF NOT EXISTS logistic_deactivated BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS logistic_deactivated_reason TEXT,
    ADD COLUMN IF NOT EXISTS logistic_can_cash BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS logistic_can_cash_reason TEXT,
    ADD COLUMN IF NOT EXISTS logistic_can_card BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS logistic_can_card_reason TEXT,
    ADD COLUMN IF NOT EXISTS logistic_can_subsidy BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS logistic_can_subsidy_reason TEXT;

ALTER TABLE parks_activation.accounts
    ADD COLUMN IF NOT EXISTS logistic_dynamic_threshold FLOAT,
    ADD COLUMN IF NOT EXISTS balances_v2_revision INTEGER;

ALTER table parks_activation.accounts
    ADD updated TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE index change_history_timestamp_index
    ON parks_activation.change_history (timestamp);

CREATE index parks_updated_index
    ON parks_activation.parks (updated);

CREATE index accounts_updated_index
    ON parks_activation.accounts (updated);
