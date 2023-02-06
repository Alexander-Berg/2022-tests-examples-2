/* V2 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

CREATE TABLE IF NOT EXISTS eats_orders_tracking.couriers_dynamic_data
(
    courier_id TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (courier_id)
);

COMMIT;
