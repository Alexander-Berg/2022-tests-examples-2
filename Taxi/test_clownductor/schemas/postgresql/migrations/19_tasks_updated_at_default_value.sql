START TRANSACTION;

UPDATE task_manager.tasks SET updated_at = EXTRACT (epoch FROM NOW()) where updated_at IS NULL;
ALTER TABLE task_manager.tasks ALTER updated_at SET NOT NULL;
ALTER TABLE task_manager.tasks ALTER updated_at SET DEFAULT EXTRACT (epoch FROM NOW());

COMMIT;
