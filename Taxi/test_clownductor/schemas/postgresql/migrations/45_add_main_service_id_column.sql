START TRANSACTION;

CREATE TYPE RELATION_TYPE AS ENUM (
    'service_database',
    'alias_main_service'
);

ALTER TABLE clownductor.related_services
    ADD COLUMN relation_type RELATION_TYPE NOT NULL DEFAULT 'service_database';

COMMIT;
