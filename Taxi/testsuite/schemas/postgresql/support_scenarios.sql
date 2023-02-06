-- Copied migrations from tools-py3 repository.

-- V001 --
CREATE SCHEMA IF NOT EXISTS scenarios;

CREATE TABLE IF NOT EXISTS scenarios.action (
    id VARCHAR(256) PRIMARY KEY,
    description text,
    text_tanker_key text,
    type text NOT NULL,
    show_message_input boolean NOT NULL DEFAULT true,
    params JSONB NOT NULL DEFAULT '{}'::JSONB,
    conditions JSONB
);

CREATE TABLE IF NOT EXISTS scenarios.actions_tree (
    parent_id VARCHAR(256) REFERENCES scenarios.action(id) ON DELETE CASCADE,
    child_id VARCHAR(256) REFERENCES scenarios.action(id) ON DELETE CASCADE,
    trigger_tanker text NOT NULL
);

-- V002 --
ALTER TABLE scenarios.actions_tree
    ADD COLUMN priority integer NOT NULL DEFAULT 0;

ALTER TABLE scenarios.action
    ADD COLUMN view text NOT NULL DEFAULT 'questionary',
    ADD COLUMN always_merge boolean NOT NULL DEFAULT FALSE,
    ADD COLUMN is_enabled boolean NOT NULL DEFAULT FALSE;

-- V003 --
ALTER TABLE scenarios.action
    ADD COLUMN view_params JSONB NOT NULL DEFAULT '{}'::JSONB;

ALTER TABLE scenarios.actions_tree
    RENAME COLUMN priority TO rank;

-- V004 --
ALTER TABLE scenarios.action
    RENAME COLUMN type TO client_callback;

ALTER TABLE scenarios.action
    RENAME COLUMN params TO client_callback_params;

ALTER TABLE scenarios.action
    RENAME COLUMN view TO type;
