START TRANSACTION;

ALTER TABLE clownductor.services ADD COLUMN deleted_at INTEGER DEFAULT NULL;
ALTER TABLE clownductor.branches ADD COLUMN deleted_at INTEGER DEFAULT NULL;

CREATE UNIQUE INDEX clownductor_project_id_service_name_type_deleted_at_idx ON clownductor.services
    (project_id, name, cluster_type, deleted_at);
DROP INDEX IF EXISTS clownductor_project_id_service_name_type_idx;

CREATE UNIQUE INDEX branches_service_id_name_key_deleted_at_idx ON clownductor.branches
    (service_id, name, deleted_at);
ALTER TABLE clownductor.branches DROP CONSTRAINT branches_service_id_name_key;

COMMIT;
