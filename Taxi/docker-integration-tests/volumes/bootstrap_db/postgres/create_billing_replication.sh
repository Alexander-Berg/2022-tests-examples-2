#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE dbbillingreplication;

\connect dbbillingreplication


------------------------------------------- CLIDS -------------------------------------------------------

CREATE TABLE public.clients (
  id TEXT,
  park_id TEXT NOT NULL,

  contracts_updated TIMESTAMP DEFAULT NULL,
  persons_updated TIMESTAMP DEFAULT NULL,

  created TIMESTAMP NOT NULL,
  updated TIMESTAMP NOT NULL,

  PRIMARY KEY (id, park_id)
);

CREATE INDEX clients_bulk_for_contracts ON public.clients (
    contracts_updated NULLS FIRST
);

CREATE INDEX clients_bulk_for_persons ON public.clients (
    persons_updated NULLS FIRST
);


------------------------------------------- CONTRACTS -------------------------------------------------------

CREATE TYPE public.CONTRACT_TYPE AS ENUM (
		'GENERAL', 'SPENDABLE'
);

CREATE TYPE public.CONTRACT_STATUS AS ENUM (
                'ACTIVE', 'INACTIVE'
);

CREATE TABLE public.contracts (
    "ID" INTEGER PRIMARY KEY,

    client_id TEXT NOT NULL,
    type CONTRACT_TYPE NOT NULL,

    "EXTERNAL_ID" TEXT,
    "PERSON_ID" INTEGER,
    "IS_ACTIVE" SMALLINT, /* BOOLEAN */
    "IS_SIGNED" SMALLINT, /* BOOLEAN */
    "IS_SUSPENDED" SMALLINT, /* BOOLEAN */
    "CURRENCY" TEXT,
    "NETTING" SMALLINT, /* BOOLEAN */
    "NETTING_PCT" TEXT,
    "LINK_CONTRACT_ID" INTEGER,
    "SERVICES" INTEGER[],
    "NDS_FOR_RECEIPT" INTEGER,
    "OFFER_ACCEPTED" SMALLINT, /* BOOLEAN */
    "NDS" INTEGER,
    "PAYMENT_TYPE" INTEGER,
    "PARTNER_COMMISSION_PCT" TEXT,
    "PARTNER_COMMISSION_PCT2" TEXT,
    "IND_BEL_NDS_PERCENT" TEXT,

    /* END_DT and FINISH_DT are logically different, this logic is best kept in backend */
    "END_DT" TIMESTAMP,
    "FINISH_DT" TIMESTAMP,
    "DT" TIMESTAMP,

    created TIMESTAMP NOT NULL,
    updated TIMESTAMP NOT NULL,

    status CONTRACT_STATUS NOT NULL DEFAULT 'ACTIVE',

    revision SERIAL
    
);

CREATE INDEX contracts_clients_fk ON public.contracts (
    client_id
);

CREATE TABLE contract_field_diffs (
		/*
			It IS supposed to be join-able with contracts.id, hence the index; however, if a contract
			is deleted, its diff is preserved for history's sake, and vice versa. Therefore, a constraint
			is not necessary.
		*/
    id INTEGER NOT NULL,
    field TEXT NOT NULL,
    /* We're not interested in types here */
    before TEXT,
    after TEXT,
		timestamp TIMESTAMP
);

CREATE INDEX contract_diffs_contracts_fk ON contract_field_diffs (
		id
);

CREATE TYPE CONTRACT_CHANGE_TYPE AS ENUM (
		'activation', 'deactivation'
);

/* Decoupled from contract_field_diffs for clarity and code simplicity */
CREATE TABLE public.contract_changes(
		id INTEGER NOT NULL,
		type CONTRACT_CHANGE_TYPE NOT NULL,
		timestamp TIMESTAMP NOT NULL
);

CREATE INDEX contract_changes_contracts_fk ON public.contract_changes (
		id
);

------------------------------------------- CONTRACTS -------------------------------------------------------

CREATE TABLE public.balances (
    /* Actually, it's returned as a string but is cast to allow for easier joining */
    "ContractID" INTEGER PRIMARY KEY,
    "Balance" TEXT,
    "CurrMonthCharge" INTEGER,
    "CommissionToPay" TEXT,
    "CurrMonthBonus" TEXT,
    "BonusLeft" TEXT,
    "ClientID" INTEGER,
    "OfferAccepted" SMALLINT, /* BOOLEAN */
    "Currency" TEXT,
    "NettingLastDt" TIMESTAMP,
    "PersonalAccountExternalID" TEXT,

    "DT" TIMESTAMP,

    created TIMESTAMP,
    updated TIMESTAMP,

    revision SERIAL
);

CREATE INDEX balances_clients_fk ON public.balances(
		"ClientID"
);

------------------------------------------- PERSONS -------------------------------------------------------

CREATE TABLE persons (
    "ID" TEXT PRIMARY KEY,
    "OWNERSHIP_TYPE" TEXT,
    "DELIVERY_TYPE" TEXT,
    "LEGAL_ADDRESS_POSTCODE" TEXT,
    "NAME" TEXT,
    "MNAME" TEXT,
    "LONGNAME" TEXT,
    "LNAME" TEXT,
    "PHONE" TEXT,
    "INN" TEXT,
    "CLIENT_ID" TEXT,
    "AUTHORITY_DOC_TYPE" TEXT,
    "FNAME" TEXT,
    "INVALID_BANKPROPS" TEXT,
    "LEGALADDRESS" TEXT,
    "TYPE" TEXT,
    "EMAIL" TEXT,
    "SIGNER_PERSON_NAME" TEXT,
    "KPP" TEXT,
    "OGRN" TEXT,
    "BIK" TEXT,
    "BANK" TEXT,
    "BANKCITY" TEXT,
    "ACCOUNT" TEXT,
    "CORRACCOUNT" TEXT,

    "DT" TIMESTAMP,

    created TIMESTAMP NOT NULL,
    updated TIMESTAMP NOT NULL,

    revision SERIAL
);

CREATE INDEX persons_clients_fk ON persons (
		"CLIENT_ID"
);

DROP SCHEMA IF EXISTS parks CASCADE;

CREATE SCHEMA parks;

ALTER TABLE public.balances SET SCHEMA parks;
ALTER TABLE public.clients SET SCHEMA parks;
ALTER TABLE public.contract_changes SET SCHEMA parks;
ALTER TABLE public.contract_field_diffs SET SCHEMA parks;
ALTER TABLE public.contracts SET SCHEMA parks;
ALTER TABLE public.persons SET SCHEMA parks;


ALTER TABLE parks.contracts ADD COLUMN "CONTRACT_TYPE" INTEGER;
ALTER TABLE parks.contracts ADD COLUMN "IND_BEL_NDS" TEXT;
EOSQL
