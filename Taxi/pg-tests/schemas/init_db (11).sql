CREATE SCHEMA IF NOT EXISTS eats_robocall;

CREATE TABLE IF NOT EXISTS eats_robocall.actions (
    token TEXT NOT NULL PRIMARY KEY,
    action_info JSONB NOT NULL,
    call_external_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS eats_robocall.idempotency_tokens(
   token TEXT PRIMARY KEY,
   call_id BIGINT NOT NULL,
   created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
   updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS eats_robocall.calls
(
    id BIGSERIAL PRIMARY KEY,
    call_external_id TEXT NOT NULL,
    ivr_flow_id TEXT NOT NULL,
    personal_phone_id TEXT NOT NULL,
    context JSONB NOT NULL,
    status TEXT NOT NULL,
    ivr_dispatcher_record_id TEXT,
    scenario JSONB NOT NULL,
    answers TEXT[] DEFAULT array[]::varchar[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
