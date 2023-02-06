BEGIN;

ALTER TABLE eats_robocall.calls
    ADD COLUMN IF NOT EXISTS answers TEXT[] DEFAULT array[]::varchar[],
    ADD COLUMN IF NOT EXISTS ivr_dispatcher_record_id TEXT,
    ADD COLUMN IF NOT EXISTS scenario JSONB NOT NULL
;

CREATE UNIQUE INDEX IF NOT EXISTS calls_call_external_id_idx ON eats_robocall.calls (call_external_id);

CREATE TABLE IF NOT EXISTS eats_robocall.actions (
    token TEXT NOT NULL PRIMARY KEY,
    action_info JSONB NOT NULL,
    call_external_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMIT;
