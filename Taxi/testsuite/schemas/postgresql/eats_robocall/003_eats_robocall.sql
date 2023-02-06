BEGIN;

CREATE INDEX IF NOT EXISTS actions_created_at_idx ON eats_robocall.actions (created_at);
CREATE INDEX IF NOT EXISTS actions_updated_at_idx ON eats_robocall.actions (updated_at);

COMMIT;
