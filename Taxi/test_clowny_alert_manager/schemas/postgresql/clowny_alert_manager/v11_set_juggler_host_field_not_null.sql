ALTER TABLE alert_manager.branches
    ALTER COLUMN basename SET NOT NULL,
    ALTER COLUMN juggler_host SET NOT NULL
;
