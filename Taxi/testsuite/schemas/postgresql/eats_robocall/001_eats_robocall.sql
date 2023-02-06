BEGIN;

CREATE SCHEMA IF NOT EXISTS eats_robocall;

CREATE TABLE IF NOT EXISTS eats_robocall.idempotency_tokens(
   token TEXT PRIMARY KEY,
   call_id BIGINT NOT NULL,
   created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
   updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idempotency_tokens_created_at_idx ON eats_robocall.idempotency_tokens (created_at);
CREATE INDEX IF NOT EXISTS idempotency_tokens_updated_at_idx ON eats_robocall.idempotency_tokens (updated_at);

-- table with calls history
CREATE TABLE IF NOT EXISTS eats_robocall.calls
(
    id BIGSERIAL PRIMARY KEY,
    call_external_id TEXT NOT NULL,
    ivr_flow_id TEXT NOT NULL,
    personal_phone_id TEXT NOT NULL,
    context JSONB NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS calls_created_at_idx ON eats_robocall.calls (created_at);
CREATE INDEX IF NOT EXISTS calls_updated_at_idx ON eats_robocall.calls (updated_at);

CREATE TYPE eats_robocall.call_v1 AS (
    call_external_id TEXT,
    ivr_flow_id TEXT,
    personal_phone_id TEXT,
    context JSONB
);

COMMIT;
