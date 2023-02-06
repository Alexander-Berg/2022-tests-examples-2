CREATE SCHEMA contractor_instant_payouts;

SET SEARCH_PATH TO contractor_instant_payouts;

CREATE DOMAIN decimal4 AS decimal(19, 4);

CREATE TABLE park_account (
  PRIMARY KEY (id),

  id                  uuid                NOT NULL,

  park_id             text                NOT NULL,

  updated_at          timestamptz         NOT NULL DEFAULT NOW(),
  created_at          timestamptz         NOT NULL DEFAULT NOW(),

  currency            text                NOT NULL,
  bank_data           jsonb               NOT NULL
);

CREATE UNIQUE INDEX park_account_secondary_key
                    ON park_account (park_id, id);

CREATE INDEX park_account_replica_idx
             ON park_account (updated_at);


CREATE TABLE contractor_card (
  PRIMARY KEY (id),
  FOREIGN KEY (park_id, account_id)
      REFERENCES park_account (park_id, id)
      ON DELETE RESTRICT ON UPDATE RESTRICT,

  id                  uuid                NOT NULL,

  park_id             text                NOT NULL,
  contractor_id       text                NOT NULL,
  account_id          uuid                NOT NULL,

  updated_at          timestamptz         NOT NULL DEFAULT NOW(),
  created_at          timestamptz         NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX contractor_card_secondary_key
                    ON contractor_card (park_id, contractor_id, id);

CREATE INDEX contractor_card_replica_idx
             ON contractor_card (updated_at);


CREATE TABLE contractor_payout (
  PRIMARY KEY (id),
  CONSTRAINT contractor_payout_park_id_fkey
      FOREIGN KEY (park_id, contractor_id, card_id)
          REFERENCES contractor_card (park_id, contractor_id, id)
          ON DELETE RESTRICT ON UPDATE RESTRICT,

  id                  uuid                NOT NULL,

  park_id             text                 NULL,
  contractor_id       text                 NULL,
  card_id             uuid                 NULL,

  updated_at          timestamptz         NOT NULL DEFAULT NOW(),
  created_at          timestamptz         NOT NULL DEFAULT NOW(),

  withdrawal_amount   decimal4             NULL,
  debit_amount        decimal4             NULL,
  debit_fee           decimal4             NULL,
  transfer_amount     decimal4             NULL,

  transfer_status     jsonb               NULL,
  transfer_fee        decimal4            NULL
);

CREATE UNIQUE INDEX contractor_payout_plist_key
                    ON contractor_payout(id);


