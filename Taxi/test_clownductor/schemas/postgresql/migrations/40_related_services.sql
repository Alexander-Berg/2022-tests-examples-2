BEGIN TRANSACTION;

CREATE TABLE clownductor.related_services (
    service_id INTEGER NOT NULL REFERENCES
        clownductor.services (id) ON DELETE CASCADE,
    related_service_id INTEGER NOT NULL REFERENCES
        clownductor.services (id) ON DELETE CASCADE,
    PRIMARY KEY (service_id, related_service_id)
);

CREATE INDEX clownductor_related_services_related_service_id
    ON clownductor.related_services (related_service_id);

COMMIT TRANSACTION;
