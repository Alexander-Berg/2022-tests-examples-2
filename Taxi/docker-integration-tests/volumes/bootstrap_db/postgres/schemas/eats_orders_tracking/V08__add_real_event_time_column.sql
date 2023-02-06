/* V3 */
/* pgmigrate-encoding: utf-8 */

BEGIN;

ALTER TABLE eats_orders_tracking.orders
    ADD COLUMN real_event_time TIMESTAMPTZ NOT NULL DEFAULT NOW();

COMMIT;
