CREATE SCHEMA dispatch;

CREATE TYPE dispatch.dispatch_status_t AS ENUM (
    'idle',
    'scheduled',
    'matching',
    'matched',
    'delivering',
    'delivered',
    'canceling',
    'canceled',
    'revoked',
    'finished',
    'rescheduling'
);

CREATE TABLE dispatch.dispatches (
    id             UUID PRIMARY KEY,
    order_id       TEXT NOT NULL UNIQUE,
    performer_id   TEXT DEFAULT NULL,

    dispatch_type  TEXT NOT NULL,
    version        INT NOT NULL,
    status         dispatch.dispatch_status_t NOT NULL,

    order_info     JSONB NOT NULL,
    performer_info JSONB DEFAULT NULL,

    updated        TIMESTAMPTZ NOT NULL default NOW(),
    status_meta    JSONB DEFAULT NULL,
    wave           INT NOT NULL DEFAULT 0,
    eta            INT NOT NULL DEFAULT 0
);

CREATE TABLE dispatch.cargo_dispatches ( 
    dispatch_id      UUID NOT NULL,
    claim_id         TEXT NOT NULL,
    is_current_claim BOOLEAN NOT NULL DEFAULT TRUE,
    status_updated   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    claim_status     TEXT NOT NULL DEFAULT 'new',
    claim_version    INT NOT NULL DEFAULT 0,
    PRIMARY KEY (dispatch_id, claim_id)
);  

CREATE TABLE dispatch.dispatches_history (
    id             UUID NOT NULL,
    order_id       TEXT NOT NULL,
    performer_id   TEXT DEFAULT NULL,

    dispatch_type  TEXT NOT NULL,
    version        INT NOT NULL,
    status         dispatch.dispatch_status_t,

    order_info     JSONB NOT NULL,
    performer_info JSONB DEFAULT NULL,

    updated        TIMESTAMPTZ NOT NULL,
    status_meta    JSONB DEFAULT NULL,
    wave           INT DEFAULT 0,
    PRIMARY KEY (id, version)
);

CREATE TABLE dispatch.dispatches_extra_info (
    dispatch_id UUID NOT NULL PRIMARY KEY,
    eta_timestamp TIMESTAMPTZ DEFAULT NULL,
    smoothed_eta_timestamp TIMESTAMPTZ DEFAULT NULL,
    smoothed_eta_eval_time TIMESTAMPTZ DEFAULT NULL,
    updated TIMESTAMPTZ NOT NULL default NOW()
);
