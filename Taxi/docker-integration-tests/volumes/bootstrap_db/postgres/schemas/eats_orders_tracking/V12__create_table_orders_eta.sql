/* V12 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

CREATE TABLE IF NOT EXISTS eats_orders_tracking.orders_eta
(
    order_nr TEXT NOT NULL,
    eta TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (order_nr)
);

CREATE INDEX IF NOT EXISTS orders_eta_updated_at_idx ON eats_orders_tracking.orders_eta (updated_at);

COMMIT;
