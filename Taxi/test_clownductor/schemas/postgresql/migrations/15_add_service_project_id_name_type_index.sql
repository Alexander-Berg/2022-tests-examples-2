START TRANSACTION;

ALTER TABLE clownductor.services DROP CONSTRAINT services_project_id_name_key;
CREATE UNIQUE INDEX clownductor_project_id_service_name_type_idx ON clownductor.services
    (project_id, name, cluster_type);

COMMIT;
