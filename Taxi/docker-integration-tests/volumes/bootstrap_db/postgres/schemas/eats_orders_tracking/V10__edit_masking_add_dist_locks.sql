/* V10 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

ALTER TABLE eats_orders_tracking.masked_courier_phone_numbers
    ALTER COLUMN phone_number DROP NOT NULL,
    ALTER COLUMN extension DROP NOT NULL,
    ALTER COLUMN ttl DROP NOT NULL,
    ADD COLUMN IF NOT EXISTS error_count SMALLINT NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS masked_courier_phone_numbers_claim_id_ttl_error_count_idx
    ON eats_orders_tracking.masked_courier_phone_numbers (claim_id, ttl, error_count);

CREATE TABLE IF NOT EXISTS eats_orders_tracking.distlocks
(
    key TEXT,
    owner TEXT,
    expiration_time TIMESTAMPTZ,
    PRIMARY KEY (key)
);

CREATE TABLE IF NOT EXISTS eats_orders_tracking.distlock_periodic_updates
(
    task_id TEXT,
    updated TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (task_id)
);

COMMIT;
