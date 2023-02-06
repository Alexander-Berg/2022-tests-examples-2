ALTER TABLE clownductor.services ADD COLUMN idempotency_token TEXT DEFAULT NULL;

CREATE UNIQUE INDEX clownductor_services_idempotency_token_unique
    ON clownductor.services (idempotency_token);
