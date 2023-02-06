/* V15 */
/* pgmigrate-encoding: utf-8 */

CREATE INDEX CONCURRENTLY IF NOT EXISTS orders_updated_at_status_is_asap_idx
    ON eats_orders_tracking.orders (updated_at, (payload->>'status'), (payload->>'is_asap'));
