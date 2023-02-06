/* V16 */
/* pgmigrate-encoding: utf-8 */

DROP INDEX CONCURRENTLY IF EXISTS eats_orders_tracking.orders_updated_at_status_is_asap_idx;

CREATE INDEX CONCURRENTLY IF NOT EXISTS orders_status_is_asap_updated_at_idx
    ON eats_orders_tracking.orders ((payload->>'status'), ((payload->>'is_asap')::bool), updated_at);
