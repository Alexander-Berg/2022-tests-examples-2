/* V2 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

CREATE TABLE IF NOT EXISTS eats_orders_tracking.masked_courier_phone_numbers
(
    claim_id TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    extension TEXT NOT NULL,
    ttl TIMESTAMPTZ NOT NULL,
    PRIMARY KEY(claim_id)
);

COMMIT;
