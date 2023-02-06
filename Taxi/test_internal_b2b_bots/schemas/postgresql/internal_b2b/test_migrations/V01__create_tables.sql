-- This migration is a duplicate of #7 migration from internal-b2b-automations,
-- because they share one DB.

CREATE SCHEMA IF NOT EXISTS internal_b2b;

CREATE TABLE IF NOT EXISTS internal_b2b.telegram_staff(
    login varchar,
    chiefs jsonb,
    department_group_id integer,
    department_group_ancestors_id jsonb,
    groups_group_id jsonb,
    is_deleted boolean,
    is_dismissed boolean,
    telegram_account varchar
);

CREATE INDEX IF NOT EXISTS telegram_staff_telegram_account_idx ON
    internal_b2b.telegram_staff(
        telegram_account
    );

CREATE INDEX IF NOT EXISTS telegram_staff_login_idx ON
    internal_b2b.telegram_staff(
        login
    );

CREATE TABLE IF NOT EXISTS internal_b2b.sf_tg_support_contracts (
    contract_id varchar,
    contract_taxi_code varchar,
    account_name varchar,
    staff_login varchar,
    full_name varchar,
    telegram_login varchar,
    lead_login varchar
);
