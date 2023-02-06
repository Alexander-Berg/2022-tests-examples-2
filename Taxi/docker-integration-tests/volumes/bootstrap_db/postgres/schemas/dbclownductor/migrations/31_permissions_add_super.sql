ALTER TABLE permissions.roles
    ADD COLUMN is_super BOOLEAN NOT NULL DEFAULT FALSE,
    DROP CONSTRAINT check_exclusive_project_or_service,
    ADD CONSTRAINT check_exclusive_project_or_service CHECK (
        CASE
            WHEN NOT is_super THEN
                (project_id IS NOT NULL OR deleted_project IS NOT NULL) <>
                (service_id IS NOT NULL OR deleted_service IS NOT NULL)
            ELSE (
                project_id IS NULL AND
                deleted_project IS NULL AND
                service_id IS NULL AND
                deleted_service IS NULL
            )
        END
    )
